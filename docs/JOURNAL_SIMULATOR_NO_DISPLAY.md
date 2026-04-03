# Журнал: симулятор запускается, сцена / окно не отображаются

Дата разбора: 2026-04-04. Окружение: macOS Apple Silicon, репозиторий `mur_ide-macos-arm`.

---

## 1) Симптомы (как у пользователя)

- `./start_simulator` или запуск из IDE: приложение стартует, но **3D-сцена не видна** / «пустой» рендер.
- В логе (`simulator.log` или вывод в терминал) в начале есть:

  `ERROR: Could not create window, root cause: 'No OpenGL support in video driver'`

- Далее сыпятся предупреждения вида **device is lost**, **Texture load while device is lost** — это **следствие**: контекст OpenGL так и не был создан.

Установка дополнительных brew-пакетов **не заменяет** отсутствие поддержки OpenGL **внутри собранной SDL**, с которой линкуется Urho3D.

---

## 2) Корневая причина (диагностика)

1. Сообщение `'No OpenGL support in video driver'` выставляется в SDL, когда для текущего video driver **нет** `GL_CreateContext`, а окно запрашивают с флагом `SDL_WINDOW_OPENGL` (см. `Urho3D/Source/ThirdParty/SDL/src/video/SDL_video.c`, ветка `SDL_CreateWindowFrom`).

2. MUR Simulator на macOS встраивает окно Qt и инициализирует GL через этот путь — нужен **десктопный OpenGL (CGL / NSOpenGL)**, а не только GLES.

3. В **встроенной SDL Urho3D** опция CMake `VIDEO_OPENGL` была завязана на условие **`NOT ARM`**. На Apple Silicon компилятор определяет **`__aarch64__`**, Urho3D помечает **`ARM=TRUE`**, поэтому на Mac ARM **`VIDEO_OPENGL` оказывался OFF**, Cocoa-слой собирался **без** полноценной ветки OpenGL → `GL_CreateContext == NULL` → ошибка выше.

4. Параллельно `VIDEO_OPENGLES` включался для **любого** ARM, что соответствовало мобильным целям, но **не отменяло** необходимость desktop GL для сценария Qt + foreign window на macOS.

Итог: это **ошибка конфигурации сборки SDL под macOS ARM**, а не «не хватает драйвера» в системе.

---

## 3) Исправление в коде (что сделано в репозитории)

Файл: `Urho3D/Source/ThirdParty/SDL/CMakeLists.txt`

- Вместо одной строки `dep_option(..., "длинное выражение со скобками", ...)` используются **предвычисленные флаги** `_SDL_DEP_VIDEO_OPENGL` / `_SDL_DEP_VIDEO_OPENGLES` и вызовы `cmake_dependent_option(...)`: у `cmake_dependent_option` четвёртый аргумент **не принимает** составное выражение со скобками так, как ожидалось при первой попытке патча (CMake завершался ошибкой `Unknown arguments specified`).

- **`VIDEO_OPENGL`**: включается, если не Android/iOS/tvOS/web **и** при этом либо не ARM, либо **Apple desktop** (`APPLE AND NOT IOS AND NOT TVOS`) — то есть **macOS на Apple Silicon** снова получает desktop OpenGL (NSOpenGL/CGL).

- **`VIDEO_OPENGLES`**: для **Apple desktop** на ARM **не** включается автоматически только из-за ARM; для Linux ARM, iOS и т.д. поведение сохраняется.

Проверка после `cmake`: в `Urho3D/build/CMakeCache.txt` должно быть `VIDEO_OPENGL:BOOL=ON` и `HAVE_VIDEO_OPENGL:INTERNAL=1`.

---

## 4) Что нужно сделать у себя после обновления файла

Пересобрать цепочку, чтобы в `libUrho3D.a` попала SDL с включённым desktop OpenGL:

1. Удалить (или пересоздать) каталог сборки Urho3D, чтобы CMake не тянул старые кэшированные флаги SDL:

   ```bash
   cd "/Users/roman/Documents/MUR IDE"   # корень репозитория
   rm -rf Urho3D/build
   ```

2. Собрать Urho3D заново:

   ```bash
   cd Urho3D
   cmake -S . -B build -G Ninja
   cmake --build build -j
   cd ..
   ```

3. Пересобрать симулятор (он линкуется с Urho3D):

   ```bash
   cd mur_simulator
   rm -rf build
   cmake -S . -B build -G Ninja -DURHO3D_HOME="$PWD/../Urho3D/build"
   cmake --build build -j
   cd ..
   ```

   (При необходимости подставьте абсолютный `URHO3D_HOME`, см. QUICKSTART/RUNBOOK.)

4. При желании пересобрать IDE (если меняли только движок/симулятор — не обязательно):

   ```bash
   cd mur_ide
   cmake -S . -B build -G Ninja -DCMAKE_PREFIX_PATH="$(brew --prefix qt)"
   cmake --build build -j
   cd ..
   ```

5. Проверка:

   ```bash
   ./start_simulator
   ```

   В логе **не** должно быть `No OpenGL support in video driver`; окно сцены должно нормально отрисовываться.

---

## 5) Следующий симптом: окно есть, камеры есть, сцена «пустая» / массовые ошибки шейдеров

**Дата:** 2026-04-04 (продолжение).

### Симптомы

- В логе **нет** `No OpenGL support in video driver`, движок пишет `Initialized renderer`, виден адаптер (например Apple M2).
- Появляются миниатюры камер, но основной вид **не** показывает нормальную сцену.
- В логе десятки строк вида:

  `Failed to compile pixel shader ... ERROR: ... 'sampler3D' : syntax error`

- Дополнительно может быть: `Could not find resource Textures/WaterNoise.dds`.

### Причина A — принудительный OpenGL 2

В `mur_simulator/sources/Ui/ApplicationWindowDesktop.cpp` для десктопа выставлялось **`EP_FORCE_GL2 = true`**, чтобы облегчить создание контекста на части macOS. После починки SDL это уже не обязательно.

При **GL2** Urho3D **не** добавляет в шейдеры `#version 150` и макрос **`GL3`** (см. `OGLShaderVariation.cpp`: это завязано на `Graphics::GetGL3Support()`). Текущие шейдеры из CoreData (`Samplers.glsl` и др.) объявляют **`uniform sampler3D`** / используют возможности, которые в таком режиме компилятор macOS отклоняет — отсюда каскад ошибок и отсутствие нормального рендера.

**Исправление:** выставить **`parameters[Urho3D::EP_FORCE_GL2] = false`**, чтобы запрашивался контекст **OpenGL 3.2 core** (на Apple Silicon он обычно доступен). Если контекст GL3 не создастся, движок **сам** пробует откат на GL2 (`OGLGraphics.cpp` после неудачного `SDL_GL_CreateContext`).

### Причина B — неверный путь к текстуре воды

В `mur_simulator/resources/Data/Materials/Environment/WaterTop.xml` было указано `Textures/WaterNoise.dds`, тогда как файл лежит как **`Textures/Water/WaterNoise.dds`**. Исправить путь в XML.

### Действия после правок

Пересобрать **только симулятор** (Urho3D пересобирать не нужно, если не трогали SDL):

```bash
cd "/Users/roman/Documents/MUR IDE/mur_simulator"
cmake --build build -j
```

Проверка: `./start_simulator` — в логе **не** должно быть массовых `Failed to compile pixel shader` с `sampler3D`; сцена должна отображаться.

---

## 6) Прочее

- Предупреждение Qt про locale `C` / US-ASCII: при желании выставить UTF-8 локаль в окружении; на рендер обычно не влияет.
- Проблемы с `URHO3D_HOME` при cmake — см. QUICKSTART: путь к **`…/Urho3D/build`** из корня репозитория.

---

## 7) Объединённый чеклист

| Этап | Симптом / цель | Действие |
|------|----------------|----------|
| A | `No OpenGL support in video driver` | Патч SDL `VIDEO_OPENGL` для macOS ARM + пересборка Urho3D и симулятора |
| B | `sampler3D` / провал компиляции шейдеров при живом GL | `EP_FORCE_GL2 = false` в `ApplicationWindowDesktop.cpp` + пересборка симулятора |
| C | `Textures/WaterNoise.dds` not found | Путь в `WaterTop.xml` → `Textures/Water/WaterNoise.dds` |

Конец журнала.
