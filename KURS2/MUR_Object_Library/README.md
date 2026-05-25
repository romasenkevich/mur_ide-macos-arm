# Библиотека 3D-объектов MUR (тема 9)

Готовая библиотека учебных объектов для симулятора MUR IDE: **22 объекта** (≥15 по ТЗ) + **3 примера полигонов**.

## Структура

```
MUR_Object_Library/
  Markers/          — маркеры и указатели (7)
  Obstacles/        — препятствия (5)
  Navigation/       — навигация (5)
  Terrain/          — рельеф (3)
  Composite/        — составные объекты (2)
  Examples/         — учебные сцены (3)
  docs/             — каталог, таблица, инструкция
  tools/            — сборка и запуск редактора
```

## Быстрый старт

### 1. Собрать / обновить файлы сцен

```bash
cd "/Users/roman/Documents/MUR IDE/KURS2/MUR_Object_Library"
python3 tools/build_library.py
```

### 2. Основной способ (использован в курсовой) — `build_library.py`

```bash
cd "/Users/roman/Documents/MUR IDE/KURS2/MUR_Object_Library"
python3 tools/build_library.py
```

Скрипт формирует XML Urho3D (примитивы, Scale, Material, иерархия) и упаковывает `.mur_scene` — эквивалент ручной сборки в редакторе сцен.

### 3. Редактор сцен Urho3D (опционально, для правки)

```bash
./tools/start_editor.sh
```

Требует собранного `Urho3D/build/bin/Urho3DPlayer`. В редакторе: **Create → Builtin object**, материалы `Materials/Objects/Colors/...`, **File → Save scene as**. Для правки готового объекта: распакуйте `.mur_scene`, **File → Load scene** → `.xml`.

### 4. Тест в симуляторе

```bash
cd "/Users/roman/Documents/MUR IDE"
./start_simulator
```

В окне симулятора:

1. **Scene → Open** (`Ctrl+O`)
2. Выберите файл, например:  
   `KURS2/MUR_Object_Library/Markers/marker_start_red.mur_scene`
3. Убедитесь, что объект виден под водой
4. **Remote mode** — управление W/A/S/D/Q/E, облет объекта

Проверка учебного полигона:

`Examples/example_markers_course.mur_scene`

### 5. Телеуправление и скриншоты для каталога

- Включите **Remote mode** в симуляторе
- Сделайте скриншоты для `docs/CATALOG.md` и плакатов по ТЗ

## Упаковка своей сцены в .mur_scene

После сохранения в редакторе `my_object.xml`:

```bash
cd /path/to/folder
echo '{"version": 1.0}' > Config.json
zip -r my_object.mur_scene Config.json my_object.xml
```

## Документация для пояснительной записки

- [docs/CATALOG.md](docs/CATALOG.md) — каталог объектов (приложение А)
- [docs/COLORS_AND_SIZES.md](docs/COLORS_AND_SIZES.md) — таблица цветов и размеров
- [docs/IMPORT_INSTRUCTIONS.md](docs/IMPORT_INSTRUCTIONS.md) — инструкция (приложение Б)

## Примечание для отчёта

Объекты собраны в формате сцен симулятора MUR (`Config.json` version 1.0, Urho3D XML).  
Основное создание — **`build_library.py`** (эквивалент редактора сцен Urho3D по ТЗ). Ручная правка в `Editor.sh` — по желанию.
