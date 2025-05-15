from typing import List, Tuple

import numpy as np
from lab2.calculations_lab2 import calc_rd, find_stabilization
from lab2.const_lab2 import MIN_POINTS_TO_CALC_RD, MIN_POINTS_TO_CALC_STAB
from utils.stand_controller import StandController
from utils.data.measurement import Measurement


class Lab2Controller:
    def __init__(self):
        self.stand = StandController()
        self.vah: List[Measurement] = []

    def measure(self) -> Measurement:
        m = self.stand.get_voltage_current()
        self.vah.append(m)
        return m

    def get_vah_arrays(self):
        u = np.array([x.u_out for x in self.vah])
        i = np.array([x.i_out_mA for x in self.vah])
        return u, i

    def compute_rd_from_lists(
        self,
        u_list: List[float],
        i_mA_list: List[float],
        n: float,
        Ut: float
    ) -> List[Tuple[float, float, float, float]]:

        u_arr = np.array(u_list)
        i_arr = np.array(i_mA_list)
        if u_arr.size < MIN_POINTS_TO_CALC_RD:
            raise ValueError(f"Недостаточно точек. Нужно ≥{MIN_POINTS_TO_CALC_RD}")
        return calc_rd(u_arr, i_arr, n, Ut)


    def compute_stabilization_from_lists(
        self,
        u_list: List[float],
        i_list: List[float],
        min_rd: float
    ) -> Tuple[int, np.ndarray, np.ndarray]:

        u = np.array(u_list)
        i = np.array(i_list)
        if u.size < MIN_POINTS_TO_CALC_STAB:
            raise ValueError(f"Недостаточно данных для анализа стабилизации. Минимум {MIN_POINTS_TO_CALC_STAB} точек")
        idx = find_stabilization(u, i, min_rd)
        return idx, u, i

    def average_rd(self, rows):
        rd_values = [t[2] for t in rows]
        rd_avg = sum(rd_values) / len(rd_values)
        return rd_avg
