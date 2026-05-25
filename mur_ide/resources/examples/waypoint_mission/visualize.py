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
    times, xs, ys, zs, _, _, _, _ = load_log_full(path)
    return times, xs, ys, zs


def load_log_full(
    path: str | Path,
) -> Tuple[
    List[float],
    List[float],
    List[float],
    List[float],
    List[float],
    List[float],
    List[float],
    List[int],
]:
    """Полная загрузка CSV-журнала (столбцы как в logger_module.LOG_HEADER)."""
    file_path = Path(path)
    times: List[float] = []
    xs: List[float] = []
    ys: List[float] = []
    zs: List[float] = []
    yaws: List[float] = []
    target_yaws: List[float] = []
    distances: List[float] = []
    wp_idx: List[int] = []

    with file_path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            times.append(float(row["Время"]))
            xs.append(float(row["X"]))
            ys.append(float(row["Y"]))
            zs.append(float(row["Z"]))
            yaws.append(float(row["Курс"]))
            target_yaws.append(float(row["Целевой_курс"]))
            distances.append(float(row["Расстояние"]))
            wp_idx.append(int(float(row["Номер_точки"])))

    return times, xs, ys, zs, yaws, target_yaws, distances, wp_idx


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


def plot_depth_and_course(
    log_path: str | Path,
    output_path: str | Path = "depth_course_plot.png",
    target_depth: float | None = None,
) -> None:
    """
    Эпюры глубины Z и курса от времени (рис. В.3 приложения).
    """
    times, _, _, zs, yaws, target_yaws, _, _ = load_log_full(log_path)
    fig, (ax_z, ax_yaw) = plt.subplots(2, 1, figsize=(10, 6), sharex=True)

    ax_z.plot(times, zs, "b-", linewidth=1.8, label="Z, м")
    if target_depth is not None:
        ax_z.axhline(target_depth, color="r", linestyle="--", linewidth=1.2, label="Заданная глубина")
    ax_z.set_ylabel("Глубина, м")
    ax_z.grid(True, linestyle="--", alpha=0.5)
    ax_z.legend(loc="upper right")

    ax_yaw.plot(times, yaws, "b-", linewidth=1.5, label="Курс, °")
    ax_yaw.plot(times, target_yaws, "r--", linewidth=1.2, alpha=0.85, label="Целевой курс, °")
    ax_yaw.set_xlabel("Время, с")
    ax_yaw.set_ylabel("Курс, °")
    ax_yaw.grid(True, linestyle="--", alpha=0.5)
    ax_yaw.legend(loc="upper right")

    fig.tight_layout()
    fig.savefig(output_path, dpi=200, facecolor="white")
    plt.close(fig)

