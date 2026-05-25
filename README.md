# MUR IDE — симулятор и скрипты (macOS ARM)

Монорепозиторий MUR IDE и **mur_simulator** для macOS (Apple Silicon): запуск IDE, симулятора, примеров Python и вспомогательных скриптов курсовых (KURS, KURS2).

Сборка с нуля — один раз, в **[RUNBOOK.md](RUNBOOK.md)**. Ниже — только **запуск уже собранного**.

## Возможности

- Запуск **MUR IDE** и **симулятора** из корня репозитория
- Примеры АНПА на Python (`mur_ide/resources/examples/`, в т.ч. миссия по waypoints)
- Генерация графики и Word для курсового **KURS** (траектории)
- Сборка библиотеки 3D-объектов и плакатов для **KURS2**

## Быстрый старт

Все команды — из корня репозитория (путь с пробелом в кавычках):

```bash
cd "/path/to/MUR IDE"   # корень клона, кавычки из‑за пробела в имени
```

| Действие | Команда |
|----------|---------|
| IDE | `./start_ide` |
| Симулятор | `./start_simulator` |
| Пример в IDE | Открыть `mur_ide/resources/examples/waypoint_mission/waypoint_mission.py` → **F5** (нужен **Remote mode** в симуляторе) |

Перед первым F5: симулятор собран, `pymurapi` установлен (см. RUNBOOK).

## Симулятор: открыть сцену библиотеки (KURS2)

```bash
./start_simulator
```

В окне: **Scene → Open** → файл, например:

`KURS2/MUR_Object_Library/Markers/marker_start_red.mur_scene`

## Скрипты KURS (траектория АНПА)

| Скрипт | Назначение |
|--------|------------|
| `python3 KURS/md_to_txt.py` | Конвертация `.md` → `.txt` для записки |
| `python3 KURS/build_docx.py` | Сборка `KURS/docx/*.docx` из текстов |
| `python3 KURS/output/draw_flowchart_2_2.py` | Блок-схема 2.2 |
| `python3 KURS/output/draw_structure_2_1.py` | Структура ПО 2.1 |
| `python3 KURS/output/draw_geometry_course.py` | Геометрия курса |
| `python3 KURS/output/draw_section_4.py` | Графика раздела 4 (логи → `KURS/output/logs/`) |
| `python3 KURS/output/draw_appendix_B.py` | Приложение В (таблица, графики) |

Подписи и скриншоты: **[KURS/ИНСТРУКЦИЯ_РИСУНКИ.txt](KURS/ИНСТРУКЦИЯ_РИСУНКИ.txt)** · тексты: `KURS/ПЗ.txt`, `KURS/info.txt`

После прогона миссии положите CSV в `KURS/output/logs/`, затем снова `draw_section_4.py`.

## Скрипты KURS2 (библиотека объектов)

```bash
cd "KURS2/MUR_Object_Library"
python3 tools/build_library.py    # все .mur_scene
cd "../.."
python3 KURS2/output/draw_graphic_materials.py   # плакаты, блок-схема 3.1, наборы А4
python3 KURS2/build_docx.py                      # Word из ПЗ
```

Опционально: `./tools/start_editor.sh` — редактор Urho3D (не обязателен для записки).

Подробнее: **[KURS2/README_LIBRARY.md](KURS2/README_LIBRARY.md)** · рисунки: **[KURS2/ИНСТРУКЦИЯ_РИСУНКИ.txt](KURS2/ИНСТРУКЦИЯ_РИСУНКИ.txt)**

## Настройка миссии waypoints (в IDE)

| Параметр | Где | Описание |
|----------|-----|----------|
| Точки маршрута | `mur_ide/resources/examples/waypoint_mission/waypoints.csv` | Координаты (ось Y CSV = Z сцены) |
| `CYCLES` | `waypoint_mission.py` | Число проходов по маршруту |
| Remote mode | Симулятор | Обязателен для управления с клавиатуры / скрипта |

## Устранение неполадок

| Проблема | Решение |
|----------|---------|
| `./start_ide` / `./start_simulator` не находит бинарник | Собрать по **RUNBOOK.md** (`mur_ide/build/mur_ide`, `mur_simulator/build/bin/simulator`) |
| F5 в IDE — ошибка импорта | `pip install` / локальная установка **pymurapi** (RUNBOOK) |
| Симулятор: чёрные объекты | Запуск из корня репо; пересборка `python3 KURS2/MUR_Object_Library/tools/build_library.py` |
| Нет графиков раздела 4 | Положить `mission_*.csv` в `KURS/output/logs/`, запустить `draw_section_4.py` |
| Путь с пробелом | Кавычки вокруг пути: `cd "/path/to/MUR IDE"` |

## Структура (главное)

| Путь | Содержимое |
|------|------------|
| `start_ide`, `start_simulator` | Запуск из корня |
| `mur_ide/resources/examples/` | Python-примеры для F5 |
| `KURS/` | Курсовой 1: ПЗ, генераторы графики |
| `KURS2/MUR_Object_Library/` | Библиотека `.mur_scene` |
| `RUNBOOK.md` | Установка и сборка (не для ежедневного запуска) |

## Ссылки

- Официальный MUR IDE: [murproject.com](https://murproject.com/#muride)
- Полная сборка на macOS ARM: **[RUNBOOK.md](RUNBOOK.md)**
