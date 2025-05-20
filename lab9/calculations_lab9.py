from typing import List, Tuple
import numpy as np

MIN_POINTS_TO_CALC_S = 2


def compute_s_values(
        Ube: np.ndarray,
        Ic: np.ndarray,
        threshold: float
) -> List[float]:

    if Ube.size < MIN_POINTS_TO_CALC_S or Ic.size < MIN_POINTS_TO_CALC_S:
        return []
    S = []
    for i in range(Ube.size - 1):
        dU = Ube[i + 1] - Ube[i]
        if abs(dU) < threshold:
            continue
        dI = Ic[i + 1] - Ic[i]
        S.append(dI / dU)
    return S


def compute_resistances(
        data: List[Tuple[float, float, float, float, float]],
        v_ohm_low: float,
        v_ohm_high: float,
        v_dyn_low: float,
        v_dyn_high: float,
        min_dI_ohm: float,
        min_dI_dyn: float
) -> List[Tuple[float, float, float]]:
    results = []
    for Uzi, I_lo, I_hi, I6, I9 in data:
        dI_ohm = (I_hi - I_lo) / 1000.0
        if abs(dI_ohm) < min_dI_ohm:
            R_ohm = None
        else:
            R_ohm = (v_ohm_high - v_ohm_low) / dI_ohm

        dI_dyn = (I9 - I6) / 1000.0
        if abs(dI_dyn) < min_dI_dyn:
            R_dyn = None
        else:
            R_dyn = (v_dyn_high - v_dyn_low) / dI_dyn

        results.append((Uzi, R_ohm, R_dyn))
    return results
