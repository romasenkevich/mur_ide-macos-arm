"""
Модуль визуализации траекторий.

Соответствует разделам 1.5, 3.6, 4.7, 5.5 ТЗ:
– построение графиков траекторий по лог‑файлам;
– отображение путевых точек и сравнений сценариев.
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Tuple

import csv
import matplotlib.pyplot as plt

from waypoints import Waypoint


def load_log(path: str | Path) -> Tuple[List[float], List[float], List[float], List[float]]:
    """
    Загрузка данных из CSV‑лога.
    Возвращает списки: времена, x, y, z.
    """
    file_path = Path(path)
    times: List[float] = []
    xs: List[float] = []
    ys: List[float] = []
    zs: List[float] = []

    with file_path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            times.append(float(row["Время"]))
            xs.append(float(row["X"]))
            ys.append(float(row["Y"]))
            zs.append(float(row["Z"]))

    return times, xs, ys, zs


def plot_trajectory(
    log_path: str | Path,
    waypoints: List[Waypoint],
    output_path: str | Path = "trajectory_plot.png",
) -> None:
    """
    Построение графика траектории по одному лог‑файлу.
    """
    _, xs, ys, _ = load_log(log_path)

    plt.figure(figsize=(8, 8))
    plt.plot(xs, ys, "b-", label="Фактическая траектория", linewidth=2)
    if waypoints:
        wx = [w[0] for w in waypoints]
        wy = [w[1] for w in waypoints]
        plt.plot(wx, wy, "ro", label="Путевые точки")
        plt.plot(wx + [wx[0]], wy + [wy[0]], "r--", label="Идеальная траектория")

    plt.xlabel("X, м")
    plt.ylabel("Y, м")
    plt.grid(True)
    plt.axis("equal")
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()


def plot_depth_over_time(
    log_path: str | Path,
    output_path: str | Path = "depth_plot.png",
) -> None:
    """
    Построение графика изменения глубины во времени.
    """
    times, _, _, zs = load_log(log_path)
    plt.figure(figsize=(8, 4))
    plt.plot(times, zs, "b-")
    plt.xlabel("Время, с")
    plt.ylabel("Глубина, м")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
    
