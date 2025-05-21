from typing import List, Dict, Tuple

import numpy as np

from lab9.calculations_lab9 import compute_s_values, compute_resistances
from lab9.const_lab9 import THRESHOLD_DELTA_U, THRESHOLD_DELTA_I, V_OHM_LOW, V_OHM_HIGH, V_DYN_LOW, V_DYN_HIGH
from utils.data.measurement import Measurement
from utils.packet_builder import PacketBuilder
from utils.stand_controller import StandController


class Lab9Controller:
    def __init__(self):
        self.stand = StandController()
        self.vh: List[Measurement] = []

        self.voltage_builder = PacketBuilder(bytes([0x20, 0x50, 0x00, 0x01, 0x02, 0x01]))

    def measure(self) -> Measurement:
        m = self.stand.get_voltage_current()
        self.vh.append(m)
        return m

    def compute_transconductance_s(
            self,
            data: Dict[float, Tuple[List[float], List[float]]]
    ) -> Dict[float, List[float]]:

        result: Dict[float, List[float]] = {}
        for Uce, (Ube_list, Ic_list) in data.items():
            Ube = np.array(Ube_list)
            Ic = np.array(Ic_list)
            S_vals = compute_s_values(Ube, Ic, THRESHOLD_DELTA_U)
            if S_vals:
                result[Uce] = S_vals
        if not result:
            raise ValueError("Нет достаточных данных для расчёта S.")
        return result

    def comp_resistances(
            self,
            data: List[Tuple[float, float, float, float, float]]
    ) -> List[Tuple[float, float, float]]:
        res = compute_resistances(
            data,
            v_ohm_low=V_OHM_LOW,
            v_ohm_high=V_OHM_HIGH,
            v_dyn_low=V_DYN_LOW,
            v_dyn_high=V_DYN_HIGH,
            min_dI_ohm=THRESHOLD_DELTA_I,
            min_dI_dyn=THRESHOLD_DELTA_I
        )
        if not res:
            raise ValueError("Нет достаточных данных для расчёта сопротивлений.")
        return res

    def set_voltage(self, voltage: float):
        packet = self.voltage_builder.build_float(voltage)
        self.stand.send_bytes(packet)