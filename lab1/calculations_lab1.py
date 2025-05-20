from typing import List, Tuple
import numpy as np
from scipy.optimize import fsolve, curve_fit


def calc_dynamic_resistance(
        u: np.ndarray,
        i_mA: np.ndarray,
        n: float,
        Ut: float
) -> List[Tuple[float, float, float, float]]:
    I = i_mA / 1000.0
    dU = u[1:] - u[:-1]
    dI = I[1:] - I[:-1]
    rd_delta = np.divide(dU, dI, out=np.full_like(dU, np.inf), where=dI != 0)
    rd_theor = np.divide(n * Ut, I[:-1], out=np.full_like(dU, np.inf), where=I[:-1] != 0)
    return list(zip(u[:-1], i_mA[:-1], rd_delta, rd_theor))


def compute_shockley_experimental(
        U: np.ndarray,
        Is: float,
        n: float,
        Rs: float,
        Ut: float
) -> np.ndarray:

    I_result = []
    I_prev = 1e-9
    for U_val in U:
        def current_eq(I):
            exponent = (U_val - I * Rs) / (n * Ut)
            exp_safe = np.exp(np.clip(exponent, -100, 100))
            return Is * (exp_safe - 1) - I

        I_solution = fsolve(current_eq, I_prev)[0]
        I_prev = I_solution
        I_result.append(I_solution * 1000.0)

    return np.array(I_result)


def shockley_model(
        u: np.ndarray,
        i_mA: np.ndarray,
        Ut: float
) -> Tuple[np.ndarray, np.ndarray, float, float]:

    if u.size == 0 or i_mA.size == 0:
        raise ValueError("Нет данных для аппроксимации")

    I = i_mA / 1000.0
    mask = I > 0
    U_fit, I_fit = u[mask], I[mask]
    if U_fit.size == 0:
        raise ValueError("Нет валидных данных для аппроксимации")

    def eq(Uv, Is, n):
        return Is * (np.exp(Uv / (n * Ut)) - 1)

    (Is_fit, n_fit), _ = curve_fit(eq, U_fit, I_fit, p0=[1e-9, 1.5])

    U_th = np.linspace(u.min(), u.max(), 300)
    I_th = eq(U_th, Is_fit, n_fit) * 1000.0
    return U_th, I_th, Is_fit, n_fit


def theoretical_dynamic_resistance(
        U_vals: np.ndarray,
        Is: float,
        n: float,
        Rs: float,
        Ut: float
) -> List[Tuple[float, float, float, float]]:

    I_result = []
    I_prev = 1e-9
    for U_val in U_vals:
        def current_eq(I):
            exponent = (U_val - I * Rs) / (n * Ut)
            exp_safe = np.exp(np.clip(exponent, -100, 100))
            return Is * (exp_safe - 1) - I

        I_solution = fsolve(current_eq, I_prev)[0]
        I_prev = I_solution
        I_result.append(I_solution * 1000)

    I_arr = np.array(I_result)

    rows = []
    for i in range(len(U_vals) - 1):
        U0, U1 = U_vals[i], U_vals[i + 1]
        I0, I1 = I_arr[i], I_arr[i + 1]
        delta_U = U1 - U0
        delta_I = (I1 - I0) * 0.001
        rd_delta = delta_U / delta_I if delta_I != 0 else float('inf')
        rd_theor = n * Ut / (I0 * 0.001) if I0 > 0 else float('inf')
        rows.append((U0, I0, rd_delta, rd_theor))
    return rows
