# MUR IDE — краткая инструкция

**Все команды — из корня репозитория** (рядом с `mur_ide/`, `Urho3D/`, `start_ide`).

### Шпаргалка (подряд)

Команды нужно вызывать строка за строкой

```bash
export ROOT="$(pwd)"
brew update && brew install cmake ninja pkg-config qt opencv glfw python@3.11 zmq
cd "./Urho3D" && cmake -S . -B build -G Ninja && cmake --build build -j && cd ..
cd "./mur_simulator" && cmake -S . -B build -G Ninja -DURHO3D_HOME="$ROOT/Urho3D/build" && cmake --build build -j && cd ..
cd "./mur_ide" && cmake -S . -B build -G Ninja -DCMAKE_PREFIX_PATH="$(brew --prefix qt)" && cmake --build build -j && cd ..
cd "./pymurapi" && python3 -m pip install -e . && cd ..
cd "$ROOT" && ./start_ide    # или: ./start_simulator
```

Ниже то же самое с пояснениями и ссылкой на полный runbook.

---

Ниже — **порядок действий** и **запуск**. Подробности, отладка и типичные ошибки — в [RUNBOOK.md](RUNBOOK.md).

Все команды выполняйте из **корня репозитория** (папка, где лежат `mur_ide/`, `Urho3D/`, `start_ide`). В примерах это `$ROOT`.

```bash
export ROOT="$(pwd)"   # находясь в корне репозитория
```

---

## Порядок установки и сборки

| Шаг | Что сделать |
|-----|-------------|
| **1** | **Xcode CLI + Homebrew:** `xcode-select --install`, затем `brew update` и `brew install cmake ninja pkg-config qt opencv glfw python@3.11 zmq` |
| **2** | **Urho3D** — первым (от него зависит симулятор): `cd "./Urho3D" && cmake -S . -B build -G Ninja && cmake --build build -j && cd ..` |
| **3** | **mur_simulator:** `cd "./mur_simulator" && cmake -S . -B build -G Ninja -DURHO3D_HOME="$ROOT/Urho3D/build" && cmake --build build -j && cd ..` — при отсутствии ссылок в `build/bin` на `Data` и `CoreData` см. RUNBOOK §3 |
| **4** | **mur_ide:** `cd "./mur_ide" && cmake -S . -B build -G Ninja -DCMAKE_PREFIX_PATH="$(brew --prefix qt)" && cmake --build build -j && cd ..` |
| **5** | **pymurapi** (для примеров Python в IDE): `cd "./pymurapi" && python3 -m pip install -e . && cd ..` |

После правок в коде пересобирайте в том же порядке: **Urho3D → mur_simulator → mur_ide**.

---

## Запуск

```bash
cd "$ROOT"
./start_ide          # IDE
./start_simulator    # симулятор отдельно (по необходимости)
```

Симулятор из IDE обычно указывают на `$ROOT/mur_ide/mur-ide.simulator` или на `$ROOT/mur_simulator/build/bin/simulator` (см. `mur_ide/settings.ini`).

Локальный скрипт в IDE: режим **Local**, пример из `mur_ide/resources/examples`, кнопка **Run**.

---

## Быстрая проверка

Откройте в IDE `mur_ide/resources/examples/smoke_test.py` и запустите — в консоли должно быть `SMOKE_TEST_OK`.
