# MUR IDE + Simulator on macOS (с нуля)

Инструкция для нового человека, который впервые поднимает проект на macOS.

## 0) Что должно быть в рабочей папке

Этот репозиторий уже содержит все нужные подпроекты. После клонирования `mur_ide-macos-arm` структура будет такой:

```text
<workspace>/        # корень клонa mur_ide-macos-arm
  mur_ide/
  mur_simulator/
  Urho3D/
  Urho3D-1.7/
  pymurapi/
  RUNBOOK.md
  start_ide
  start_simulator
```

Пример клонирования (замените `<username>` на свой GitHub-логин, а `<dir>` — на желаемую папку):

```bash
mkdir -p <dir>
cd <dir>
git clone https://github.com/<username>/mur_ide-macos-arm.git
cd mur_ide-macos-arm
```

---

## 1) Системные зависимости (macOS)

```bash
xcode-select --install
brew update
brew install cmake ninja pkg-config qt opencv glfw python@3.11 zmq
```

Проверка:

```bash
cmake --version
ninja --version
python3 --version
```

---

## 2) Сборка Urho3D

```bash
cd <workspace>/Urho3D
cmake -S . -B build -G Ninja
cmake --build build -j
```

---

## 3) Сборка mur_simulator

```bash
cd <workspace>/mur_simulator
cmake -S . -B build -G Ninja \
  -DURHO3D_HOME=<workspace>/Urho3D/build
cmake --build build -j
```

**Важно:** После сборки убедитесь, что в `mur_simulator/build/bin/` есть символические ссылки или папки:
- `Data` → должна указывать на `mur_simulator/resources/Data`
- `CoreData` → должна указывать на `Urho3D/bin/CoreData`

Если ссылок нет, создайте их:
```bash
cd <workspace>/mur_simulator/build/bin
ln -sf ../../resources/Data Data
ln -sf ../../../Urho3D/bin/CoreData CoreData
```

Код симулятора автоматически найдёт правильные пути к ресурсам относительно расположения бинарника, но наличие этих ссылок упрощает работу.

---

## 4) Сборка mur_ide

```bash
cd <workspace>/mur_ide
cmake -S . -B build -G Ninja \
  -DCMAKE_PREFIX_PATH="$(brew --prefix qt)"
cmake --build build -j
```

---

## 5) Установка pymurapi (для Python-скриптов в IDE)

Рекомендуется в тот же Python, который будет использовать IDE:

```bash
cd <workspace>/pymurapi
python3 -m pip install -e .
python3 -c "import pymurapi; print('pymurapi ok')"
```

---

## 6) Запуск

### Запуск из корня репозитория (рекомендуется)

```bash
cd <workspace>          # корень mur_ide-macos-arm
./start_ide             # запускает mur_ide
./start_simulator       # отдельно запускает симулятор (при необходимости)
```

### Запуск по старой схеме (из подпроектов)

```bash
cd <workspace>/mur_ide
./build/mur_ide
```

### Связка IDE → симулятор

В IDE путь к симулятору должен указывать на:

- `<workspace>/mur_ide/mur-ide.simulator` (скрипт-обертка, лежит в папке IDE),
  или напрямую
- `<workspace>/mur_simulator/build/bin/simulator`

### Локальный запуск скрипта

1. Переключить режим на `Local`.
2. Открыть пример из `resources/examples`.
3. Нажать `Run`.

---

## 7) Быстрая проверка, что всё ок

- Открыть `mur_ide/resources/examples/smoke_test.py` и запустить.
- Должны быть видны строки в консоли IDE + `SMOKE_TEST_OK`.
- Запуск сцены в симуляторе должен открывать окно без белого/черного квадрата и без рендера в четверть экрана.

---

## 8) Частые проблемы

### `ModuleNotFoundError: No module named 'pymurapi'`

```bash
cd <workspace>/pymurapi
python3 -m pip install -e .
```

Проверьте, что IDE использует тот же Python (`Paths/python` в `settings.ini`).

### Не запускается симулятор из IDE

Проверьте путь `Paths/simulator` в `mur_ide/settings.ini`.

### После обновления кода не стартует/странный UI

Пересоберите по порядку:
1. `Urho3D`
2. `mur_simulator`
3. `mur_ide`

---

## 9) Локальные файлы (не коммитить)

- `build/`
- `settings.ini`
- `.DS_Store`
- `simulator.log`

Эти файлы уже добавлены в `.gitignore`.
