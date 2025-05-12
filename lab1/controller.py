from typing import Literal, Tuple, List

import numpy as np

from lab1.const import MIN_POINTS_TO_CALC_R_D, U_T
from measurement import Measurement
from lab1.calculations import calc_dynamic_resistance, compute_shockley_experimental, shockley_model, \
    theoretical_dynamic_resistance
from stand_controller import StandController

Target = Literal['si', 'sch']


class Lab1Controller:
    def __init__(self):
        self.stand = StandController()

        self.si_data: list[Measurement] = []
        self.sch_data: list[Measurement] = []

    def add_measurement(self, target: Target) -> Measurement:
        m = Measurement(1, 2, 3) #self.stand.get_voltage_current()
        if target == 'si':
            self.si_data.append(m)
        else:
            self.sch_data.append(m)
        return m

    def get_measurements(self, target: Target) -> list[Measurement]:
        return self.si_data if target == 'si' else self.sch_data

    def calculate_dynamic_resistance(
            self,
            u: List[float],
            i_mA: List[float],
            n_value: float
    ) -> List[Tuple[float, float, float, float]]:

        if len(u) < MIN_POINTS_TO_CALC_R_D:
            raise ValueError(f"Нужно как минимум {MIN_POINTS_TO_CALC_R_D} точек")
        u_arr = np.array(u)
        i_arr = np.array(i_mA)
        return calc_dynamic_resistance(u_arr, i_arr, n_value, U_T)

    def compute_exp_theor_vah(
            self,
            u: List[float],
            i_mA: List[float],
            Is: float,
            n: float,
            Rs: float,
            Ut: float
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, str]:

        u_arr = np.array(u)
        i_arr = np.array(i_mA)

        if u_arr.size == 0 or i_arr.size == 0:
            raise ValueError("Недостаточно данных для сравнения")

        I_th = compute_shockley_experimental(u_arr, Is, n, Rs, Ut)

        label = f"Is={Is:.2e} A, n={n:.2f}, Rs={Rs:.3f} Ω"

        return u_arr, i_arr, u_arr, I_th, label

    def get_shockley_data(
            self,
            u_list: List[float],
            i_list: List[float],
            Ut: float
    ) -> Tuple[np.ndarray, np.ndarray, float, float]:

        u = np.array(u_list)
        i_mA = np.array(i_list)
        return shockley_model(u, i_mA, Ut)

    def compute_theoretical_rd(
            self,
            u_list: List[float],
            Is: float,
            n: float,
            Rs: float,
            Ut: float
    ) -> List[Tuple[float, float, float, float]]:

        U_vals = np.array(u_list)
        if U_vals.size < 2:
            raise ValueError("Недостаточно точек для расчёта теоретического rd")
        return theoretical_dynamic_resistance(U_vals, Is, n, Rs, Ut)




