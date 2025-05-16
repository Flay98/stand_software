import numpy as np
from typing import List, Tuple


def calc_rd(u: np.ndarray, i_mA: np.ndarray, n: float, Ut: float) -> List[Tuple[float, float, float, float]]:
    I = i_mA / 1000.0
    dU = u[1:] - u[:-1]
    dI = I[1:] - I[:-1]
    rd_delta = np.divide(dU, dI, out=np.full_like(dU, np.inf), where=dI != 0)
    rd_theor = np.divide(n * Ut, I[:-1], out=np.full_like(dU, np.inf), where=I[:-1] != 0)
    return list(zip(u[:-1], i_mA[:-1], rd_delta, rd_theor))


def find_stabilization(u: np.ndarray, i_mA: np.ndarray, min_rd: float) -> int:
    I = i_mA / 1000.0
    for idx in range(len(u) - 1):
        dU = u[idx + 1] - u[idx]
        dI = I[idx + 1] - I[idx]
        if dI == 0: continue
        if dU / dI < min_rd: return idx
    return -1
