# Приложение Б. Инструкция по использованию библиотеки

## 1. Открыть один объект для просмотра

1. Запустите симулятор: `./start_simulator` из корня репозитория MUR IDE.
2. **Scene → Open** (`Ctrl+O`).
3. Выберите файл, например `Markers/marker_start_red.mur_scene`.
4. Проверьте видимость объекта; при необходимости включите **Remote mode** и облетите аппаратом.

## 2. Добавить объект в новую учебную сцену (редактор Urho3D)

1. Запустите `./tools/start_editor.sh`.
2. **File → New scene** (или загрузите пустую/базовую сцену).
3. **File → Load node as replicated** — укажите XML из распакованного `.mur_scene`:
   ```bash
   unzip -d /tmp/obj Markers/marker_start_red.mur_scene
   ```
   Загрузите `/tmp/obj/marker_start_red.xml`, выделите узел `LibraryObject` и дочерние объекты.
4. Альтернатива: откройте объект целиком, скопируйте узел `LibraryObject` (**Edit → Copy node**), вставьте в целевую сцену (**Paste**).
5. Переместите (**Move**), масштабируйте (**Scale**), поверните (**Rotate**).
6. **File → Save scene** → упакуйте в `.mur_scene` (Config.json + XML).

## 3. Группировка составных объектов

1. Создайте примитивы (Create → Builtin object).
2. Выделите все части в иерархии (Ctrl+клик).
3. Сгруппируйте под одним родителем (перетащите узлы на общий родитель `LibraryObject`).
4. Сохраните как один файл сцены.

## 4. Сборка полигона из библиотеки без редактора

Откройте готовые примеры в `Examples/`:

- `example_markers_course.mur_scene`
- `example_obstacle_lane.mur_scene`
- `example_navigation_track.mur_scene`

Или пересоберите библиотеку:

```bash
python3 tools/build_library.py
```

## 5. Тестирование (раздел 4 ТЗ)

| Шаг | Действие |
|-----|----------|
| 4.1 | Открыть каждый `.mur_scene`, проверить отображение |
| 4.2 | Открыть `Examples/example_markers_course.mur_scene` |
| 4.3 | Remote mode, пролёт вдоль маркеров |
| 4.4 | Оценить читаемость с разных ракурсов |
| 4.5 | При необходимости изменить размер/цвет в редакторе и пересохранить |

## 6. Пути к материалам

В симуляторе используются материалы из:

`mur_simulator/resources/Data/Materials/Objects/Colors/`

При сохранении сцен в редакторе указывайте те же пути, что в каталоге.
