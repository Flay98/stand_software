import numpy as np
from typing import List, Tuple


def find_stabilization_index(u_load: np.ndarray, threshold: float) -> int:
    for i in range(len(u_load) - 1):
        if abs(u_load[i + 1] - u_load[i]) < threshold:
            return i
    return -1


def calc_stabilization_coefficients(
        u_pit: np.ndarray,
        u_load: np.ndarray,
        start: int
) -> List[float]:
    k_vals = []
    for i in range(max(0, start - 1), len(u_load) - 1):
        dp = u_pit[i + 1] - u_pit[i]
        dl = u_load[i + 1] - u_load[i]
        avg_p = (u_pit[i + 1] + u_pit[i]) / 2
        avg_l = (u_load[i + 1] + u_load[i]) / 2
        if dl != 0 and avg_p != 0 and avg_l != 0:
            k_vals.append((dp / avg_p) / (dl / avg_l))
    return k_vals


def compute_stabilization_coefficient(
        u_pit_list: List[float],
        u_load_list: List[float],
        min_points: int,
        threshold: float
) -> Tuple[int, List[float], float]:
    if len(u_load_list) < min_points:
        raise ValueError(f"Нужно ≥{min_points} точек")
    u_pit = np.array(u_pit_list)
    u_load = np.array(u_load_list)
    start = find_stabilization_index(u_load, threshold)
    if start < 0:
        raise ValueError("Участок стабилизации не найден")
    k_vals = calc_stabilization_coefficients(u_pit, u_load, start)
    if not k_vals:
        raise ValueError("Нет ни одного коэффициента")
    return start, k_vals, float(np.mean(k_vals))


def input_power(u_pit: float, i_pit: float) -> float:
    return u_pit * i_pit * 0.001


def output_power(u_load: float, i_load: float) -> float:
    return u_load * i_load * 0.001


def efficiency(p_in: float, p_out: float) -> float:
    return p_out / p_in if p_in != 0 else 0.0


def stabilization_current(i_pit: float, i_load: float) -> float:
    return i_pit - i_load


def compute_stabilizer_metrics(
        data: List[Tuple[int, float, float, float, float]]
) -> Tuple[
    List[Tuple[int, float]],
    List[Tuple[int, float]],
    List[Tuple[int, float]],
    List[Tuple[int, float]]
]:
    if not data:
        raise ValueError("Нет данных для расчёта метрик")
    pin = [(col, input_power(u, i, ))
           for col, u, i, *_ in data]
    pout = [(col, output_power(u_l, i_l))
            for col, *_, u_l, i_l in data]
    eta = []
    ist = []
    for col, u_p, i_p, u_l, i_l in data:
        p_in = input_power(u_p, i_p)
        p_out = output_power(u_l, i_l)
        eta.append((col, efficiency(p_in, p_out)))
        ist.append((col, stabilization_current(i_p, i_l)))
    return pin, pout, eta, ist
