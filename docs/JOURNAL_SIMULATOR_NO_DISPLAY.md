# Журнал правок: симулятор, IDE, Python (macOS ARM)

Репозиторий: `mur_ide-macos-arm`. Файл ведётся как **история решённых проблем** и **что именно менялось в коде/доках**. Дата последнего обновления: 2026-04-04.

---

## 1. Симулятор: «No OpenGL support in video driver», пустой экран

**Симптом:** `./start_simulator` стартует, но нет 3D; в логе `Could not create window… No OpenGL support in video driver`.

**Причина:** В SDL внутри Urho3D опция `VIDEO_OPENGL` отключалась для любого `ARM` (в т.ч. Apple Silicon). Для встраивания окна Qt нужен desktop OpenGL; без него у Cocoa-драйвера SDL нет `GL_CreateContext`.

**Исправление:** `Urho3D/Source/ThirdParty/SDL/CMakeLists.txt` — предвычисляемые флаги и `cmake_dependent_option`, чтобы на **Apple desktop** при aarch64 включался `VIDEO_OPENGL`, а GLES не подменял этот сценарий.

**Действия:** `rm -rf Urho3D/build`, пересборка Urho3D, затем `mur_simulator` с корректным `URHO3D_HOME` (путь к `Urho3D/build`).

---

## 2. Симулятор: окно есть, шейдеры не компилируются (`sampler3D`)

**Симптом:** Рендерер инициализируется, но лавина `Failed to compile pixel shader` / `'sampler3D' : syntax error`.

**Причина:** В `mur_simulator/sources/Ui/ApplicationWindowDesktop.cpp` было `EP_FORCE_GL2 = true`. В режиме GL2 Urho3D не включает GLSL 150 / `GL3` в преамбуле шейдеров, а шейдеры CoreData используют `sampler3D`.

**Исправление:** `EP_FORCE_GL2 = false` (запрос GL 3.2 core; при неудаче движок сам откатывается к GL2).

**Ресурс:** `mur_simulator/resources/Data/Materials/Environment/WaterTop.xml` — путь к текстуре `Textures/Water/WaterNoise.dds` → `Textures/Water/WaterNoise.dds`.

---

## 3. IDE: запуск симулятора — `execve: No such file or directory`

**Симптом:** В логе IDE `Simulator: mur-ide.simulator`, затем `Child process set up failed: execve: No such file or directory`.

**Причина:** На Unix `QProcess` использует `execvp`: имя **без символа `/`** ищется в **PATH**, а не рядом с исполняемым файлом.

**Исправление:** `mur_ide/sources/SimulatorController.cpp` — функция `resolveSimulatorPath()`: для имён без `/` подставляется абсолютный путь к `mur-ide.simulator` относительно `applicationDirPath()` и `../` (типичная схема `mur_ide/build/mur_ide` + `mur_ide/mur-ide.simulator`).

**Действия:** Пересборка **только** `mur_ide`.

---

## 4. Python: `ModuleNotFoundError: No module named 'cv2'`

**Симптом:** Запуск примеров из IDE, падение при `import pymurapi` → `cv2`.

**Причина:** `brew install opencv` даёт библиотеку для C++, не модуль Python. Нужен **`opencv-python`** в том же интерпретаторе, что использует IDE (`Paths/python` / `python3` в логе).

**Исправление в репо:** `pymurapi/setup.py` — в `install_requires` добавлен `opencv-python`.

**Действия у себя:** `python3 -m pip install opencv-python` (или тот же полный путь к Python, что в IDE); при необходимости `pip install -e pymurapi` заново.

**Документация:** `QUICKSTART.md` — раздел «Python и примеры в IDE».

---

## 5. Python 3.14 / NumPy: `fromstring` binary mode removed

**Симптом:** В терминале при `./start_ide` и работе pymurapi с симулятором поток падает с:

`ValueError: The binary mode of fromstring is removed, use frombuffer instead`

(стек в `pymurapi/pymurapi/simulator.py`, `_update`.)

**Причина:** В новых версиях NumPy убрали двоичный режим `numpy.fromstring`; для массива байт из ZMQ нужен **`numpy.frombuffer`**.

**Исправление:** `pymurapi/pymurapi/simulator.py` — строки приёма JPEG с камер:

- было: `np.fromstring(self.front_socket.recv(), dtype='uint8')` (и для bottom);
- стало: `np.frombuffer(..., dtype=np.uint8)`.

**Действия:** Переустановка pymurapi не обязательна при editable-режиме — достаточно сохранённых файлов; перезапустить IDE/скрипт.

---

## 6. Краткий указатель файлов

| Тема | Файл(ы) |
|------|---------|
| SDL OpenGL на Mac ARM | `Urho3D/Source/ThirdParty/SDL/CMakeLists.txt` |
| GL3 / шейдеры симулятора | `mur_simulator/sources/Ui/ApplicationWindowDesktop.cpp` |
| Текстура воды | `mur_simulator/resources/Data/Materials/Environment/WaterTop.xml` |
| Запуск симулятора из IDE | `mur_ide/sources/SimulatorController.cpp` |
| Зависимости pymurapi | `pymurapi/setup.py`, `pymurapi/pymurapi/simulator.py` |
| Краткая инструкция | `QUICKSTART.md` |

Конец журнала.
