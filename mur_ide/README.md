# MUR IDE

![screenshot](https://robocenter.net/media/files/mur-ide.png)

__[Загрузить (для Windows)](https://murproject.com/#muride)__ | [Проект MUR](https://murproject.com/)

Среда для работы с аппаратами [Центра Робототехники](https://robocenter.net/):

- Разработка кода на Python и запуск скриптов на аппаратах __[MiddleAUV](https://robocenter.net/goods/kit/middleauv/)__ и __[MiddleUSV](https://robocenter.net/goods/kit/middleusvnew/)__, а также в [симуляторе](https://github.com/murproject/mur_simulator).
- Просмотр телеметрии с аппаратов, управление с геймпадом и просмотр изображения с камер.

## Сборка

Инструкции по сборке представлены [на данной странице](https://wiki.murproject.com/ru/MurIDE/building-ide).

### macOS (Apple Silicon и Intel)

Базовая последовательность для сборки из исходников:

```bash
xcode-select --install
brew update
brew install cmake ninja pkg-config opencv glfw qt
cmake -S . -B build -G Ninja -DCMAKE_PREFIX_PATH="$(brew --prefix qt)"
cmake --build build -j
```

Запуск после сборки:

```bash
./build/mur_ide
```

Если не находится Python или симулятор, укажите пути в `settings.ini`:

- `Paths/python` (например, `python3`)
- `Paths/simulator` (полный путь до бинарника симулятора)