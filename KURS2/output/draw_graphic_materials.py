#!/usr/bin/env python3
"""
Графический материал KURS2 (tech_task.txt, п. 3): плакаты 1–5.
Запуск: python3 KURS2/output/draw_graphic_materials.py

Плакаты 1–2, 4–5 — чертежи/схемы (matplotlib).
Плакат 3 — блок-схема процесса создания объектов (ГОСТ 19.701-90).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, Rectangle, Circle, Polygon, FancyArrowPatch
import numpy as np

plt.rcParams.update(
    {
        "font.family": "serif",
        "font.serif": ["Times New Roman", "Times", "DejaVu Serif"],
    }
)

OUT_DIR = Path(__file__).resolve().parent
DPI = 150
FLOW_DPI = 200

# Форматы (дюймы)
A4_P = (8.27, 11.69)  # портрет
A4_L = (11.69, 8.27)  # альбом
A1_L = (23.39, 16.54)  # альбом

C = {
    "red": "#c0392b",
    "green": "#27ae60",
    "yellow": "#f1c40f",
    "blue": "#2980b9",
    "orange": "#e67e22",
    "purple": "#8e44ad",
    "cyan": "#16a085",
    "gray": "#7f8c8d",
    "black": "#2c3e50",
    "white": "#ecf0f1",
}


def _save(fig: plt.Figure, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=DPI, facecolor="white", bbox_inches="tight", pad_inches=0.25)
    svg = path.with_suffix(".svg")
    fig.savefig(svg, facecolor="white", bbox_inches="tight", pad_inches=0.25)
    plt.close(fig)
    print(f"OK: {path}")


def _dim_h(ax, x0: float, x1: float, y: float, label: str, *, drawing: bool = False) -> None:
    col = "#000" if drawing else "#333"
    lw = 0.9 if drawing else 1.2
    gap = 0.06 if drawing else 0.08
    if drawing:
        # выносные линии
        for x in (x0, x1):
            ax.plot([x, x], [y - 0.25, y], color=col, lw=0.6, linestyle="-")
    ax.annotate(
        "",
        xy=(x1, y),
        xytext=(x0, y),
        arrowprops=dict(arrowstyle="<->", color=col, lw=lw),
    )
    ax.text((x0 + x1) / 2, y + gap, label, ha="center", va="bottom", fontsize=9, color=col)


def _dim_v(ax, x: float, y0: float, y1: float, label: str, *, drawing: bool = False) -> None:
    col = "#000" if drawing else "#333"
    lw = 0.9 if drawing else 1.2
    gap = 0.1 if drawing else 0.12
    if drawing:
        for y in (y0, y1):
            ax.plot([x - 0.2, x], [y, y], color=col, lw=0.6)
    ax.annotate(
        "",
        xy=(x, y1),
        xytext=(x, y0),
        arrowprops=dict(arrowstyle="<->", color=col, lw=lw),
    )
    ax.text(x - gap, (y0 + y1) / 2, label, ha="right", va="center", fontsize=9, rotation=90, color=col)


def poster_01() -> None:
    """Плакат 1 — постановка задачи, А4 портрет."""
    fig = plt.figure(figsize=A4_P, dpi=DPI)
    ax = fig.add_axes([0.06, 0.04, 0.88, 0.92])
    ax.axis("off")

    blocks = [
        ("Постановка задачи", 18, True),
        (
            "Создание библиотеки простых 3D-объектов для учебных сцен\n"
            "в симуляторе MUR IDE",
            14,
            False,
        ),
        ("Цель", 13, True),
        (
            "Библиотека маркеров, препятствий, навигационной разметки, рельефа и составных "
            "моделей для ускоренной сборки учебных полигонов и отработки управления АНПА.",
            11,
            False,
        ),
        ("Задачи", 13, True),
        (
            "1. Анализ типовых элементов сцен и объектов базовой поставки.\n"
            "2. Проектирование номенклатуры, цветов и размеров (≥12–15 объектов).\n"
            "3. Реализация в редакторе сцен, сохранение .mur_scene по папкам.\n"
            "4. Каталог, таблица цветов/размеров, инструкция импорта.\n"
            "5. Примеры полигонов и проверка в симуляторе.",
            11,
            False,
        ),
        ("Функциональные требования", 13, True),
        (
            "• Примитивы: Box, Sphere, Cylinder, Cone, Plane; материалы Objects/Colors.\n"
            "• Модульность: один объект — один файл; масштаб 1:10…1:20.\n"
            "• Габариты относительно MiddleAUV (~0,5 м): маркеры 0,5 м, стойки 2–2,5 м, "
            "проём ворот ~2,5 м.\n"
            "• Документация и 2–3 учебные сцены в Examples/.",
            11,
            False,
        ),
        ("Номенклатура по группам (22 объекта)", 13, True),
        (
            "Markers (8) — старт, финиш, waypoint×4, стрелка, маркер глубины\n"
            "Obstacles (5) — стойка, балка, ворота, угол, лабиринт\n"
            "Navigation (5) — линия, зоны старта/финиша, цифра 1, буй\n"
            "Terrain (3) — камень, растительность, труба\n"
            "Composite (2) — опора моста, «затонувший» объект\n"
            "Examples (3) — курс маркеров, полоса препятствий, трасса",
            11,
            False,
        ),
    ]

    y = 0.98
    for text, size, bold in blocks:
        ax.text(
            0.5,
            y,
            text,
            transform=ax.transAxes,
            ha="center",
            va="top",
            fontsize=size,
            fontweight="bold" if bold else "normal",
            linespacing=1.35,
        )
        y -= 0.11 if bold else 0.14

    ax.add_patch(
        FancyBboxPatch(
            (0.08, 0.02),
            0.84,
            0.12,
            boxstyle="round,pad=0.02",
            linewidth=1,
            edgecolor="#555",
            facecolor="#f8f8f8",
            transform=ax.transAxes,
        )
    )
    ax.text(
        0.5,
        0.08,
        "KURS2/MUR_Object_Library/  ·  python3 tools/build_library.py",
        transform=ax.transAxes,
        ha="center",
        va="center",
        fontsize=10,
        color="#333",
    )
    _save(fig, OUT_DIR / "01_постановка_библиотеки_A4.png")


def _drawing_frame(ax) -> None:
    """Рамка поля чертежа."""
    ax.add_patch(
        Rectangle(
            (0.02, 0.02),
            0.96,
            0.96,
            transform=ax.transAxes,
            fill=False,
            edgecolor="#000",
            linewidth=0.8,
        )
    )


def _patch_drawing(ax, patch: mpatches.Patch) -> None:
    patch.set_facecolor("white")
    patch.set_edgecolor("#000")
    patch.set_linewidth(1.6)
    patch.set_hatch("////")
    ax.add_patch(patch)


def _draw_marker_simple(ax, title: str, shape: str, color: str, dims: str) -> None:
    ax.set_xlim(-0.2, 1.2)
    ax.set_ylim(-0.2, 1.2)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(title, fontsize=11, fontweight="bold", pad=6)
    if shape == "cube":
        r = Rectangle((0.25, 0.25), 0.5, 0.5, facecolor=color, edgecolor="#333", lw=1.2)
        ax.add_patch(r)
        _dim_h(ax, 0.25, 0.75, 0.15, "0,5 м")
        _dim_v(ax, 0.15, 0.25, 0.75, "0,5 м")
    elif shape == "sphere":
        ax.add_patch(Circle((0.5, 0.5), 0.28, facecolor=color, edgecolor="#333", lw=1.2))
        ax.annotate("", xy=(0.78, 0.5), xytext=(0.5, 0.5), arrowprops=dict(arrowstyle="<->", lw=1.2))
        ax.text(0.64, 0.58, "Ø0,5 м", fontsize=9)
    else:
        ax.add_patch(
            Rectangle((0.32, 0.2), 0.36, 0.6, facecolor=color, edgecolor="#333", lw=1.2)
        )
        _dim_h(ax, 0.32, 0.68, 0.12, "Ø0,35")
        _dim_v(ax, 0.12, 0.2, 0.8, "h0,5")
    ax.text(0.5, -0.05, dims, ha="center", fontsize=8, color="#444", transform=ax.transData)


def _draw_marker_drawing(ax, title: str, shape: str, note: str) -> None:
    """Ч/б эскиз простого маркера (вид спереди)."""
    ax.set_xlim(-0.15, 1.15)
    ax.set_ylim(-0.25, 1.15)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_facecolor("white")
    _drawing_frame(ax)
    ax.set_title(title, fontsize=11, fontweight="bold", pad=8, color="#000")
    if shape == "cube":
        _patch_drawing(ax, Rectangle((0.28, 0.28), 0.48, 0.48))
        _dim_h(ax, 0.28, 0.76, 0.12, "0,5", drawing=True)
        _dim_v(ax, 0.12, 0.28, 0.76, "0,5", drawing=True)
        ax.text(0.52, 0.52, "0,5×0,5×0,5", ha="center", va="center", fontsize=8, color="#000")
    elif shape == "sphere":
        ax.add_patch(
            Circle((0.52, 0.52), 0.26, fill=False, edgecolor="#000", linewidth=1.6)
        )
        ax.plot([0.26, 0.78], [0.52, 0.52], color="#000", lw=0.6, linestyle="--")
        ax.plot([0.52, 0.52], [0.26, 0.78], color="#000", lw=0.6, linestyle="--")
        _dim_h(ax, 0.26, 0.78, 0.08, "Ø0,5", drawing=True)
    else:
        # цилиндр — вид сбоку (прямоугольник + осевые)
        _patch_drawing(ax, Rectangle((0.34, 0.22), 0.36, 0.58))
        ax.plot([0.52, 0.52], [0.22, 0.8], color="#000", lw=0.6, linestyle="--")
        _dim_h(ax, 0.34, 0.7, 0.1, "Ø0,35", drawing=True)
        _dim_v(ax, 0.08, 0.22, 0.8, "0,5", drawing=True)
    ax.text(0.52, -0.12, note, ha="center", fontsize=7.5, color="#000")


def _draw_arrow_drawing(ax) -> None:
    ax.set_title("Стрелка-указатель (составной)", fontsize=11, fontweight="bold", color="#000", pad=8)
    ax.set_xlim(-0.15, 1.65)
    ax.set_ylim(-0.35, 0.85)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_facecolor("white")
    _drawing_frame(ax)
    _patch_drawing(ax, Rectangle((0.05, 0.28), 0.95, 0.18))
    _patch_drawing(
        ax,
        Polygon([[1.0, 0.18], [1.38, 0.37], [1.0, 0.56]], closed=True),
    )
    ax.plot([0.05, 1.38], [0.37, 0.37], color="#000", lw=0.6, linestyle="--")
    _dim_h(ax, 0.05, 1.0, 0.06, "1,0", drawing=True)
    _dim_h(ax, 1.0, 1.38, 0.68, "0,4", drawing=True)
    ax.text(0.05, 0.48, "основание", fontsize=7, color="#000")
    ax.text(1.15, 0.62, "наконечник", fontsize=7, color="#000")
    ax.text(0.72, -0.22, "1,0×0,2×0,1 · 0,4×0,4×0,1 м", ha="center", fontsize=7.5, color="#000")


def _draw_gate_drawing(ax) -> None:
    ax.set_title("Ворота (составной)", fontsize=11, fontweight="bold", color="#000", pad=8)
    ax.set_xlim(-0.35, 3.05)
    ax.set_ylim(-0.25, 2.55)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_facecolor("white")
    _drawing_frame(ax)
    _patch_drawing(ax, Rectangle((0.38, 0), 0.18, 2.0))
    _patch_drawing(ax, Rectangle((2.17, 0), 0.18, 2.0))
    _patch_drawing(ax, Rectangle((0.28, 1.93), 2.45, 0.12))
    ax.plot([0.47, 2.35], [0, 0], color="#000", lw=0.6)  # линия дна
    _dim_v(ax, 0.15, 0, 2.0, "2,0", drawing=True)
    _dim_h(ax, 0.38, 2.35, 2.3, "2,5", drawing=True)
    _dim_h(ax, 0.56, 2.17, 1.05, "≈2,5", drawing=True)
    ax.text(1.35, 0.12, "проём", ha="center", fontsize=8, color="#000")


def _draw_digit_drawing(ax) -> None:
    ax.set_title("Цифра «1» (навигация)", fontsize=11, fontweight="bold", color="#000", pad=8)
    ax.set_xlim(-0.15, 0.55)
    ax.set_ylim(-0.12, 1.25)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_facecolor("white")
    _drawing_frame(ax)
    _patch_drawing(ax, Rectangle((0.18, 0.08), 0.1, 0.95))
    _dim_v(ax, 0.02, 0.08, 1.03, "1,0", drawing=True)
    _dim_h(ax, 0.18, 0.28, 0.02, "0,1", drawing=True)
    ax.text(0.23, 0.55, "Box", ha="center", fontsize=7, color="#000", rotation=90)


def poster_02() -> None:
    """Плакат 2 — эскизы и размеры (чертёж ч/б), А4 альбом."""
    fig, axes = plt.subplots(2, 3, figsize=A4_L, dpi=DPI, facecolor="white")
    fig.suptitle(
        "Эскизы и размеры основных типов объектов библиотеки MUR",
        fontsize=14,
        fontweight="bold",
        y=0.98,
        color="#000",
    )
    _draw_marker_drawing(axes[0, 0], "Старт (куб)", "cube", "marker_start_red · Red")
    _draw_marker_drawing(axes[0, 1], "Финиш (сфера)", "sphere", "marker_finish_green · Green")
    _draw_marker_drawing(axes[0, 2], "Waypoint (цилиндр)", "cyl", "marker_waypoint_*")
    _draw_arrow_drawing(axes[1, 0])
    _draw_gate_drawing(axes[1, 1])
    _draw_digit_drawing(axes[1, 2])
    fig.text(
        0.5,
        0.02,
        "Чертёжные эскизы. Ось Y — вверх (Urho3D). Размеры в метрах. Масштаб сцен 1:10…1:20.",
        ha="center",
        fontsize=9,
        color="#000",
    )
    plt.subplots_adjust(left=0.04, right=0.98, top=0.88, bottom=0.08, hspace=0.38, wspace=0.28)
    _save(fig, OUT_DIR / "02_эскизы_объектов_A4.png")


# --- Блок-схема (плакат 3), ГОСТ 19.701-90 ---
@dataclass(frozen=True)
class _ShapeBounds:
    top: float
    bottom: float
    center: float


_FC_X = 4.1
_FC_Y_TOP = 15.8
_FC_FS = 15
_FC_FS_TERM = 16
_FC_BOX_W = 4.2
_FC_BOX_H = _FC_BOX_W * 2 / 3
_FC_TERM_H = (_FC_BOX_W * 0.75) * 2 / 3
_FC_SKEW = 0.24
_FC_GAP = 0.42
_FC_ARROW = 12
_FC_LW = 1.6

_FLOW_LABELS = {
    "io_start": "Запись объекта\nв build_library.py\n(OBJECTS)",
    "primitive": "Примитив Urho3D:\nBox, Sphere,\nCylinder…",
    "setup": "Scale, Material,\nимя узла,\nположение",
    "composite": "Составной объект:\nнесколько примитивов,\nкоординаты",
    "save": "XML + Config.json\n→ .mur_scene",
    "test": "Проверка в\nсимуляторе:\nScene → Open",
    "library": "Каталог\nMUR_Object_\nLibrary/",
}


def _fc_text(ax, y: float, text: str) -> None:
    n = text.count("\n") + 1
    fs = _FC_FS_TERM if n == 1 else _FC_FS
    ax.text(_FC_X, y, text, ha="center", va="center", fontsize=fs, linespacing=0.88)


def _fc_arrow_down(ax, y_tail: float, y_head: float) -> None:
    ax.add_patch(
        FancyArrowPatch(
            (_FC_X, y_tail),
            (_FC_X, y_head),
            arrowstyle="-|>",
            mutation_scale=_FC_ARROW,
            linewidth=_FC_LW,
            color="black",
            shrinkA=0,
            shrinkB=0,
            clip_on=False,
        )
    )


def _fc_terminal(ax, y: float, text: str) -> _ShapeBounds:
    w, h = _FC_BOX_W, _FC_TERM_H
    ax.add_patch(
        FancyBboxPatch(
            (_FC_X - w / 2, y - h / 2),
            w,
            h,
            boxstyle=f"round,pad=0,rounding_size={h / 2}",
            fill=False,
            ec="black",
            lw=_FC_LW,
        )
    )
    _fc_text(ax, y, text)
    return _ShapeBounds(y + h / 2, y - h / 2, y)


def _fc_process(ax, y: float, text: str) -> _ShapeBounds:
    w, h = _FC_BOX_W, _FC_BOX_H
    ax.add_patch(
        Rectangle((_FC_X - w / 2, y - h / 2), w, h, fill=False, ec="black", lw=_FC_LW)
    )
    _fc_text(ax, y, text)
    return _ShapeBounds(y + h / 2, y - h / 2, y)


def _fc_io(ax, y: float, text: str) -> _ShapeBounds:
    w, h = _FC_BOX_W, _FC_BOX_H
    hh, hw = h / 2, w / 2
    pts = [
        (_FC_X - hw + _FC_SKEW, y - hh),
        (_FC_X + hw + _FC_SKEW, y - hh),
        (_FC_X + hw - _FC_SKEW, y + hh),
        (_FC_X - hw - _FC_SKEW, y + hh),
    ]
    ax.add_patch(Polygon(pts, closed=True, fill=False, ec="black", lw=_FC_LW))
    _fc_text(ax, y, text)
    return _ShapeBounds(y + hh, y - hh, y)


def _fc_link(ax, upper: _ShapeBounds, lower: _ShapeBounds) -> None:
    _fc_arrow_down(ax, upper.bottom, lower.top)


def _fc_below(prev: _ShapeBounds, half_h: float) -> float:
    return prev.bottom - _FC_GAP - half_h


def poster_03() -> None:
    """Плакат 3 — блок-схема процесса создания объектов в редакторе, А4 портрет."""
    fig, ax = plt.subplots(figsize=A4_P, dpi=FLOW_DPI)
    ax.set_aspect("equal")
    ax.axis("off")

    s0 = _fc_terminal(ax, _FC_Y_TOP, "Начало")
    half = _FC_BOX_H / 2

    y = _fc_below(s0, half)
    s1 = _fc_io(ax, y, _FLOW_LABELS["io_start"])
    _fc_link(ax, s0, s1)

    prev = s1
    for key in ("primitive", "setup", "composite", "save"):
        y = _fc_below(prev, half)
        s = _fc_process(ax, y, _FLOW_LABELS[key])
        _fc_link(ax, prev, s)
        prev = s

    y = _fc_below(prev, half)
    s_test = _fc_io(ax, y, _FLOW_LABELS["test"])
    _fc_link(ax, prev, s_test)

    y = _fc_below(s_test, half)
    s_lib = _fc_process(ax, y, _FLOW_LABELS["library"])
    _fc_link(ax, s_test, s_lib)

    y_end = _fc_below(s_lib, _FC_TERM_H / 2)
    s_end = _fc_terminal(ax, y_end, "Конец")
    _fc_link(ax, s_lib, s_end)

    pad_x = _FC_BOX_W / 2 + _FC_SKEW + 0.5
    ax.set_xlim(_FC_X - pad_x, _FC_X + pad_x)
    ax.set_ylim(s_end.bottom - 0.5, s0.top + 0.55)

    ax.text(
        _FC_X,
        s0.top + 0.38,
        "Технологическая схема создания объекта библиотеки",
        ha="center",
        va="bottom",
        fontsize=13,
        fontweight="bold",
    )

    fig.subplots_adjust(left=0.1, right=0.9, top=0.96, bottom=0.03)
    path = OUT_DIR / "03_процесс_редактора_A4.png"
    path.parent.mkdir(parents=True, exist_ok=True)
    save_kw = dict(dpi=FLOW_DPI, facecolor="white", pad_inches=0.15)
    fig.savefig(path, **save_kw)
    fig.savefig(path.with_suffix(".svg"), **save_kw)
    plt.close(fig)
    print(f"OK: {path}")


def _icon_ax(ax, kind: str, color: str) -> None:
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    if kind == "cube":
        ax.add_patch(Rectangle((0.25, 0.2), 0.5, 0.55, facecolor=color, edgecolor="#333"))
    elif kind == "sphere":
        ax.add_patch(Circle((0.5, 0.48), 0.28, facecolor=color, edgecolor="#333"))
    elif kind == "cyl":
        ax.add_patch(Rectangle((0.3, 0.15), 0.4, 0.65, facecolor=color, edgecolor="#333"))
    elif kind == "arrow":
        ax.add_patch(Rectangle((0.1, 0.42), 0.55, 0.16, facecolor=color, edgecolor="#333"))
        ax.add_patch(Polygon([[0.65, 0.32], [0.92, 0.5], [0.65, 0.68]], facecolor=color, edgecolor="#333"))
    elif kind == "pole":
        ax.add_patch(Rectangle((0.42, 0.05), 0.16, 0.88, facecolor=color, edgecolor="#333"))
    elif kind == "beam":
        ax.add_patch(Rectangle((0.05, 0.42), 0.9, 0.16, facecolor=color, edgecolor="#333"))
    elif kind == "gate":
        ax.add_patch(Rectangle((0.2, 0.05), 0.12, 0.85, facecolor=color, edgecolor="#333"))
        ax.add_patch(Rectangle((0.68, 0.05), 0.12, 0.85, facecolor=color, edgecolor="#333"))
        ax.add_patch(Rectangle((0.15, 0.82), 0.7, 0.08, facecolor=color, edgecolor="#333"))
    elif kind == "line":
        ax.add_patch(Rectangle((0.05, 0.46), 0.9, 0.08, facecolor=color, edgecolor="#333"))
    elif kind == "zone":
        ax.add_patch(Rectangle((0.1, 0.15), 0.8, 0.7, facecolor=color, edgecolor="#333", alpha=0.5))
    elif kind == "rock":
        ax.add_patch(Circle((0.5, 0.45), 0.32, facecolor=color, edgecolor="#333"))
    elif kind == "cone":
        ax.add_patch(Polygon([[0.5, 0.82], [0.22, 0.18], [0.78, 0.18]], facecolor=color, edgecolor="#333"))
    elif kind == "buoy":
        ax.plot([0.5, 0.5], [0.12, 0.42], color=C["black"], lw=2)
        ax.add_patch(Circle((0.5, 0.58), 0.22, facecolor=color, edgecolor="#333"))
    elif kind == "pier":
        ax.add_patch(Rectangle((0.22, 0.12), 0.18, 0.55, facecolor=color, edgecolor="#333"))
        ax.add_patch(Rectangle((0.6, 0.12), 0.18, 0.55, facecolor=color, edgecolor="#333"))
        ax.add_patch(Rectangle((0.12, 0.58), 0.76, 0.14, facecolor=color, edgecolor="#333"))
    elif kind == "wreck":
        ax.add_patch(Rectangle((0.18, 0.28), 0.64, 0.38, facecolor=C["orange"], edgecolor="#333"))
        ax.add_patch(Rectangle((0.55, 0.38), 0.12, 0.45, facecolor=C["black"], edgecolor="#333"))
        ax.add_patch(Rectangle((0.22, 0.32), 0.1, 0.35, facecolor=C["black"], edgecolor="#333"))
    elif kind == "composite":
        ax.add_patch(Rectangle((0.15, 0.2), 0.7, 0.55, facecolor=color, edgecolor="#333"))
        ax.add_patch(Rectangle((0.3, 0.55), 0.4, 0.12, facecolor=C["orange"], edgecolor="#333"))


# (файл, описание, kind, color, размер для подписи)
CatalogItem = Tuple[str, str, str, str, str]

CATALOG: List[Tuple[str, str, str, str, str]] = [
    # group, file, desc, kind, color key
    ("Markers", "marker_start_red", "Стартовый маркер", "cube", "red"),
    ("", "marker_finish_green", "Финишный маркер", "sphere", "green"),
    ("", "marker_waypoint_yellow", "Промежуточная точка", "cyl", "yellow"),
    ("", "marker_waypoint_blue", "Промежуточная точка", "cyl", "blue"),
    ("", "marker_waypoint_orange", "Промежуточная точка", "cyl", "orange"),
    ("", "marker_waypoint_purple", "Промежуточная точка", "cyl", "purple"),
    ("", "marker_direction_arrow", "Указатель направления", "arrow", "yellow"),
    ("", "marker_depth_pole", "Маркер глубины", "pole", "cyan"),
    ("Obstacles", "obstacle_pole_red", "Вертикальная стойка", "pole", "red"),
    ("", "obstacle_beam_horizontal", "Горизонтальная балка", "beam", "orange"),
    ("", "obstacle_gate", "Ворота", "gate", "red"),
    ("", "obstacle_corner_L", "Угол Г-образный", "composite", "red"),
    ("", "obstacle_maze_walls", "Фрагмент лабиринта", "composite", "black"),
    ("Navigation", "nav_track_line_white", "Линия трассы", "line", "white"),
    ("", "nav_zone_start", "Зона старта", "zone", "green"),
    ("", "nav_zone_finish", "Зона финиша", "zone", "red"),
    ("", "nav_digit_1", "Цифра 1", "pole", "yellow"),
    ("", "nav_buoy", "Буй", "sphere", "cyan"),
    ("Terrain", "terrain_rock_gray", "Камень", "rock", "gray"),
    ("", "terrain_plant_cone", "Растительность", "cone", "green"),
    ("", "terrain_pipe_straight", "Труба", "beam", "orange"),
    ("Composite", "composite_bridge_pier", "Опора моста", "composite", "black"),
    ("", "composite_wreck_simple", "Затонувший объект", "composite", "orange"),
]

GROUP_SETS: dict[str, dict] = {
    "Markers": {
        "title": "Группа Markers — маркеры и указатели",
        "folder": "Markers/",
        "cols": 4,
        "items": [
            ("marker_start_red", "Стартовый маркер", "cube", "red", "0,5³ м"),
            ("marker_finish_green", "Финишный маркер", "sphere", "green", "Ø0,5 м"),
            ("marker_waypoint_yellow", "Промежуточная точка", "cyl", "yellow", "Ø0,35 h0,5"),
            ("marker_waypoint_blue", "Промежуточная точка", "cyl", "blue", "Ø0,35 h0,5"),
            ("marker_waypoint_orange", "Промежуточная точка", "cyl", "orange", "Ø0,35 h0,5"),
            ("marker_waypoint_purple", "Промежуточная точка", "cyl", "purple", "Ø0,35 h0,5"),
            ("marker_direction_arrow", "Указатель направления", "arrow", "yellow", "1,0+0,4 м"),
            ("marker_depth_pole", "Маркер глубины", "pole", "cyan", "h≈2 м"),
        ],
    },
    "Obstacles": {
        "title": "Группа Obstacles — препятствия",
        "folder": "Obstacles/",
        "cols": 5,
        "items": [
            ("obstacle_pole_red", "Вертикальная стойка", "pole", "red", "Ø0,2 h2,5"),
            ("obstacle_beam_horizontal", "Горизонтальная балка", "beam", "orange", "3×0,25×0,25"),
            ("obstacle_gate", "Ворота", "gate", "red", "проём ~2,5"),
            ("obstacle_corner_L", "Угол Г-образный", "composite", "red", "2×0,2"),
            ("obstacle_maze_walls", "Фрагмент лабиринта", "composite", "black", "h≈1,8"),
        ],
    },
    "Navigation": {
        "title": "Группа Navigation — навигационные элементы",
        "folder": "Navigation/",
        "cols": 5,
        "items": [
            ("nav_track_line_white", "Линия трассы", "line", "white", "6×0,03×0,15"),
            ("nav_zone_start", "Зона старта", "zone", "green", "2×2 м"),
            ("nav_zone_finish", "Зона финиша", "zone", "red", "2×2 м"),
            ("nav_digit_1", "Цифра 1", "pole", "yellow", "h1,0"),
            ("nav_buoy", "Буй", "buoy", "cyan", "сфера+ножка"),
        ],
    },
    "Terrain": {
        "title": "Группа Terrain — рельеф и фон",
        "folder": "Terrain/",
        "cols": 3,
        "items": [
            ("terrain_rock_gray", "Камень (деформ. сфера)", "rock", "gray", "≈0,8 м"),
            ("terrain_plant_cone", "Растительность (конус)", "cone", "green", "h≈0,8"),
            ("terrain_pipe_straight", "Трубопровод (цилиндр)", "beam", "orange", "L≈3 м"),
        ],
    },
    "Composite": {
        "title": "Группа Composite — составные объекты",
        "folder": "Composite/",
        "cols": 2,
        "items": [
            ("composite_bridge_pier", "Мостовая опора", "pier", "black", "2,2×1,5 м"),
            ("composite_wreck_simple", "Затонувший объект", "wreck", "orange", "корпус+трубы"),
        ],
    },
}


def _scene_set_markers(ax) -> None:
    ax.set_title("Набор объектов группы (вид сверху, условно)", fontsize=14, fontweight="bold", pad=8)
    ax.set_xlim(-5.5, 5.5)
    ax.set_ylim(-2, 2)
    ax.set_aspect("equal")
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.plot([-5, 5], [-0.4, -0.4], color="#bdc3c7", lw=4, zorder=1)
    pts = [
        (-4, 0, C["red"], "s", "старт"),
        (-2, 0, C["yellow"], "o", "WP"),
        (0, 0, C["blue"], "o", ""),
        (2, 0, C["orange"], "o", ""),
        (4, 0, C["green"], "s", "финиш"),
    ]
    for x, y, col, m, lb in pts:
        ax.scatter([x], [y], c=col, s=140 if m == "s" else 90, marker=m, edgecolors="#333", zorder=3)
        if lb:
            ax.text(x, -1.1, lb, ha="center", fontsize=10)
    ax.arrow(0.5, 1.0, 2.0, 0, head_width=0.25, head_length=0.35, fc=C["yellow"], ec="#333", lw=1.2)
    ax.text(1.5, 1.35, "стрелка", ha="center", fontsize=10)
    ax.plot([4.5, 4.5], [0, 1.5], color=C["cyan"], lw=3)
    ax.text(4.5, 1.7, "глубина", ha="center", fontsize=10)


def _scene_set_obstacles(ax) -> None:
    ax.set_title("Набор объектов группы (вид сбоку, условно)", fontsize=14, fontweight="bold", pad=8)
    ax.set_xlim(-0.5, 12)
    ax.set_ylim(-0.5, 3.5)
    ax.set_aspect("equal")
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.add_patch(Rectangle((0.8, 0), 0.3, 2.5, facecolor=C["red"], edgecolor="#333"))
    ax.text(0.95, -0.35, "стойка", ha="center", fontsize=10)
    ax.add_patch(Rectangle((2.5, 1.5), 3, 0.25, facecolor=C["orange"], edgecolor="#333"))
    ax.text(4, 1.15, "балка", ha="center", fontsize=10)
    ax.add_patch(Rectangle((6.8, 0), 0.2, 2, facecolor=C["red"], edgecolor="#333"))
    ax.add_patch(Rectangle((8.8, 0), 0.2, 2, facecolor=C["red"], edgecolor="#333"))
    ax.add_patch(Rectangle((6.7, 1.9), 2.4, 0.12, facecolor=C["red"], edgecolor="#333"))
    ax.text(7.9, -0.35, "ворота", ha="center", fontsize=10)
    ax.add_patch(Rectangle((10, 0), 1.8, 0.2, facecolor=C["red"], edgecolor="#333"))
    ax.add_patch(Rectangle((10, 0), 0.2, 1.8, facecolor=C["red"], edgecolor="#333"))
    ax.text(10.5, -0.35, "угол", ha="center", fontsize=10)
    for i, x in enumerate([11.2, 11.6, 11.4, 11.8]):
        ax.add_patch(Rectangle((x, 0), 0.08, 1.5, facecolor=C["black"], edgecolor="#333"))
    ax.text(11.5, -0.35, "лабиринт", ha="center", fontsize=10)


def _scene_set_navigation(ax) -> None:
    ax.set_title("Набор объектов группы (вид сверху, условно)", fontsize=14, fontweight="bold", pad=8)
    ax.set_xlim(-0.5, 11)
    ax.set_ylim(-0.5, 5.5)
    ax.set_aspect("equal")
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.plot([1, 9], [1.2, 1.2], color="#95a5a6", lw=5)
    ax.plot([1, 9], [4, 4], color="#95a5a6", lw=5)
    ax.add_patch(Rectangle((0.3, 0.2), 2, 1.2, facecolor=C["green"], alpha=0.4, edgecolor=C["green"]))
    ax.text(1.3, 0.05, "старт", fontsize=10)
    ax.add_patch(Rectangle((7.7, 0.2), 2, 1.2, facecolor=C["red"], alpha=0.4, edgecolor=C["red"]))
    ax.text(8.2, 0.05, "финиш", fontsize=10)
    ax.add_patch(Circle((5, 2.6), 0.3, facecolor=C["cyan"], edgecolor="#333"))
    ax.plot([5, 5], [2.6, 1.5], color=C["black"], lw=2)
    ax.text(5.4, 2.9, "буй", fontsize=10)
    ax.add_patch(Rectangle((4.85, 2.0), 0.12, 0.8, facecolor=C["yellow"], edgecolor="#333"))
    ax.text(5.5, 2.0, "«1»", fontsize=11, fontweight="bold")


def _scene_set_terrain(ax) -> None:
    ax.set_title("Набор объектов группы (вид сверху, условно)", fontsize=14, fontweight="bold", pad=8)
    ax.set_xlim(-1, 10)
    ax.set_ylim(-1, 4)
    ax.set_aspect("equal")
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.add_patch(Circle((2, 1.5), 0.7, facecolor=C["gray"], edgecolor="#333"))
    ax.text(2, 0.4, "камень", ha="center", fontsize=10)
    ax.add_patch(Polygon([[5, 2.8], [4.2, 0.8], [5.8, 0.8]], facecolor=C["green"], edgecolor="#333"))
    ax.text(5, 0.4, "растительность", ha="center", fontsize=10)
    ax.add_patch(Rectangle((7.5, 1.2), 2.5, 0.2, facecolor=C["orange"], edgecolor="#333"))
    ax.text(8.7, 0.4, "труба", ha="center", fontsize=10)


def _scene_set_composite(ax) -> None:
    ax.set_title("Набор объектов группы (вид сбоку, условно)", fontsize=14, fontweight="bold", pad=8)
    ax.set_xlim(-0.5, 10)
    ax.set_ylim(-0.5, 3)
    ax.set_aspect("equal")
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.add_patch(Rectangle((1.2, 0), 0.45, 1.6, facecolor=C["black"], edgecolor="#333"))
    ax.add_patch(Rectangle((2.5, 0), 0.45, 1.6, facecolor=C["black"], edgecolor="#333"))
    ax.add_patch(Rectangle((0.9, 1.45), 2.4, 0.2, facecolor=C["black"], edgecolor="#333"))
    ax.text(2.1, -0.35, "опора моста", ha="center", fontsize=10)
    ax.add_patch(Rectangle((6.2, 0.35), 1.4, 0.7, facecolor=C["orange"], edgecolor="#333"))
    ax.add_patch(Rectangle((7.0, 0.5), 0.18, 0.9, facecolor=C["black"], edgecolor="#333"))
    ax.add_patch(Rectangle((6.0, 0.45), 0.15, 0.55, facecolor=C["black"], edgecolor="#333"))
    ax.text(7.0, -0.35, "затонувший объект", ha="center", fontsize=10)


_SCENE_DRAW = {
    "Markers": _scene_set_markers,
    "Obstacles": _scene_set_obstacles,
    "Navigation": _scene_set_navigation,
    "Terrain": _scene_set_terrain,
    "Composite": _scene_set_composite,
}

_GROUP_SLUG = {
    "Markers": "Markers",
    "Obstacles": "Obstacles",
    "Navigation": "Navigation",
    "Terrain": "Terrain",
    "Composite": "Composite",
}

_GROUP_FS_TITLE = 22
_GROUP_FS_NAME = 15
_GROUP_FS_DESC = 13
_GROUP_FS_SIZE = 12


def _draw_group_cell(ax, fname: str, desc: str, kind: str, ck: str, size: str) -> None:
    _icon_ax(ax, kind, C.get(ck, C["gray"]))
    ax.text(0.5, -0.12, fname, transform=ax.transAxes, ha="center", fontsize=_GROUP_FS_NAME, fontweight="bold")
    ax.text(0.5, -0.26, desc, transform=ax.transAxes, ha="center", fontsize=_GROUP_FS_DESC, color="#333")
    ax.text(0.5, -0.40, size, transform=ax.transAxes, ha="center", fontsize=_GROUP_FS_SIZE, color="#555")


def poster_group_sets() -> None:
    """Рисунки наборов объектов по группам (А4 альбом)."""
    for key, data in GROUP_SETS.items():
        items: List[CatalogItem] = data["items"]
        cols = data["cols"]
        rows = int(np.ceil(len(items) / cols))
        fig = plt.figure(figsize=A4_L, dpi=DPI)
        fig.suptitle(data["title"], fontsize=_GROUP_FS_TITLE, fontweight="bold", y=0.98)
        fig.text(
            0.5,
            0.94,
            f"MUR_Object_Library/{data['folder']} · {len(items)} объектов · масштаб 1:10…1:20",
            ha="center",
            fontsize=13,
            color="#444",
        )
        gs = fig.add_gridspec(
            1 + rows,
            cols,
            height_ratios=[1.15] + [1.0] * rows,
            left=0.04,
            right=0.98,
            top=0.88,
            bottom=0.05,
            hspace=0.55,
            wspace=0.28,
        )
        ax_scene = fig.add_subplot(gs[0, :])
        _SCENE_DRAW[key](ax_scene)
        for i, (fname, desc, kind, ck, size) in enumerate(items):
            r, c = divmod(i, cols)
            ax = fig.add_subplot(gs[1 + r, c])
            _draw_group_cell(ax, fname, desc, kind, ck, size)
        slug = _GROUP_SLUG[key]
        out = OUT_DIR / f"04_набор_{slug}_A4.png"
        _save(fig, out)


def poster_04() -> None:
    """Плакат 4 — каталог всех объектов, А1."""
    n = len(CATALOG)
    cols, rows = 6, 4
    fig = plt.figure(figsize=A1_L, dpi=DPI)
    fig.suptitle(
        "Каталог объектов библиотеки MUR_Object_Library (22 объекта)",
        fontsize=36,
        fontweight="bold",
        y=0.98,
    )
    gs = fig.add_gridspec(rows, cols, left=0.02, right=0.99, top=0.88, bottom=0.06, hspace=0.88, wspace=0.32)
    group_title = ""
    idx = 0
    for r in range(rows):
        for c in range(cols):
            if idx >= n:
                break
            grp, fname, desc, kind, ck = CATALOG[idx]
            if grp:
                group_title = grp
            ax = fig.add_subplot(gs[r, c])
            _icon_ax(ax, kind, C.get(ck, C["gray"]))
            ax.set_title(group_title if c == 0 and grp else "", fontsize=20, fontweight="bold", loc="left", color="#2c3e50")
            ax.text(0.5, -0.16, fname, transform=ax.transAxes, ha="center", fontsize=18, fontweight="bold")
            ax.text(0.5, -0.38, desc, transform=ax.transAxes, ha="center", fontsize=16, color="#222")
            idx += 1
    fig.text(
        0.5,
        0.01,
        "Скриншоты из симулятора можно заменить иконки: KURS2/screenshots/catalog/<имя>.png",
        ha="center",
        fontsize=16,
        color="#666",
    )
    _save(fig, OUT_DIR / "04_каталог_объектов_A1.png")


def _example_markers(ax) -> None:
    ax.set_title("example_markers_course", fontsize=12, fontweight="bold")
    ax.set_xlim(-5, 5)
    ax.set_ylim(-2, 2)
    ax.set_aspect("equal")
    ax.grid(True, alpha=0.3)
    pts = [(-4, 0, C["red"], "s"), (-2, 0, C["yellow"], "o"), (0, 0, C["blue"], "o"), (2, 0, C["orange"], "o"), (4, 0, C["green"], "s")]
    for x, y, col, m in pts:
        ax.scatter([x], [y], c=col, s=120 if m == "s" else 80, marker=m, edgecolors="#333", zorder=3)
    ax.plot([-4.5, 4.5], [-0.3, -0.3], color=C["white"], lw=6, solid_capstyle="round", zorder=1)
    ax.plot([-4.5, 4.5], [-0.3, -0.3], color="#bdc3c7", lw=2, zorder=2)
    ax.text(-4, -1.2, "старт", fontsize=8, ha="center")
    ax.text(4, -1.2, "финиш", fontsize=8, ha="center")
    ax.set_xlabel("X, м")
    ax.set_ylabel("Y, м")


def _example_obstacles(ax) -> None:
    ax.set_title("example_obstacle_lane", fontsize=12, fontweight="bold")
    ax.set_xlim(-1, 8)
    ax.set_ylim(-1, 4)
    ax.set_aspect("equal")
    ax.grid(True, alpha=0.3)
    ax.add_patch(Rectangle((1, 0), 0.25, 2.5, facecolor=C["red"], edgecolor="#333"))
    ax.add_patch(Rectangle((3, 1.2), 3, 0.25, facecolor=C["orange"], edgecolor="#333"))
    ax.add_patch(Rectangle((6.5, 0), 0.2, 2, facecolor=C["red"], edgecolor="#333"))
    ax.add_patch(Rectangle((7.7, 0), 0.2, 2, facecolor=C["red"], edgecolor="#333"))
    ax.add_patch(Rectangle((6.4, 1.9), 2.5, 0.15, facecolor=C["red"], edgecolor="#333"))
    ax.text(1.1, -0.5, "стойка", fontsize=8)
    ax.text(4, 0.9, "балка", fontsize=8)
    ax.text(7.2, -0.5, "ворота", fontsize=8)


def _example_nav(ax) -> None:
    ax.set_title("example_navigation_track", fontsize=12, fontweight="bold")
    ax.set_xlim(-1, 10)
    ax.set_ylim(-1, 6)
    ax.set_aspect("equal")
    ax.grid(True, alpha=0.3)
    ax.plot([1, 9], [1, 1], color="#bdc3c7", lw=3)
    ax.plot([1, 9], [4, 4], color="#bdc3c7", lw=3)
    ax.add_patch(Rectangle((0.5, 0.3), 2, 1.5, facecolor=C["green"], alpha=0.35, edgecolor=C["green"]))
    ax.add_patch(Rectangle((7.5, 0.3), 2, 1.5, facecolor=C["red"], alpha=0.35, edgecolor=C["red"]))
    ax.add_patch(Circle((5, 2.5), 0.25, facecolor=C["cyan"], edgecolor="#333"))
    ax.plot([5, 5], [2.5, 1.8], color=C["black"], lw=2)
    ax.text(1.5, 0.1, "зона старта", fontsize=8)
    ax.text(8, 0.1, "зона финиша", fontsize=8)
    ax.text(5.3, 2.6, "буй", fontsize=8)


def poster_05() -> None:
    """Плакат 5 — примеры использования, А1."""
    fig, axes = plt.subplots(1, 3, figsize=A1_L, dpi=DPI)
    fig.suptitle(
        "Примеры использования библиотеки — учебные сцены Examples/",
        fontsize=18,
        fontweight="bold",
        y=0.96,
    )
    _example_markers(axes[0])
    _example_obstacles(axes[1])
    _example_nav(axes[2])
    notes = [
        "Курс маркеров: старт → 3 waypoint → финиш + линия трассы.\n"
        "Задание: проплыть по цветам в Remote mode.",
        "Полоса препятствий: стойка, балка, проём ворот.\n"
        "Задание: облёт с запасом по глубине.",
        "Навигационная трасса: линии, зоны, буй.\n"
        "Задание: движение между линиями, финиш в красной зоне.",
    ]
    for ax, note in zip(axes, notes):
        ax.text(0.5, -0.18, note, transform=ax.transAxes, ha="center", va="top", fontsize=10, linespacing=1.3)
    fig.text(
        0.5,
        0.02,
        "Схемы сверху; для отчёта замените скриншотами: Examples/*.mur_scene в симуляторе",
        ha="center",
        fontsize=11,
        color="#555",
    )
    plt.subplots_adjust(left=0.05, right=0.98, top=0.88, bottom=0.14, wspace=0.2)
    _save(fig, OUT_DIR / "05_примеры_полигонов_A1.png")


def main() -> None:
    poster_01()
    poster_02()
    poster_03()
    poster_04()
    poster_group_sets()
    poster_05()
    print("\nГотово.")


if __name__ == "__main__":
    main()
