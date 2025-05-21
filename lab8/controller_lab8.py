from typing import List, Tuple

from lab8.calculations_lab8 import compute_avg_beta
from utils.packet_builder import PacketBuilder
from utils.stand_controller import StandController
from utils.data.measurement import Measurement


class Lab8Controller:
    def __init__(self):
        self.stand = StandController()
        self.vh: List[Measurement] = []

        self.voltage_builder = PacketBuilder(bytes([0x20, 0x50, 0x00, 0x01, 0x02, 0x01]))

    def measure(self) -> Measurement:
        m = self.stand.get_voltage_current()
        self.vh.append(m)
        return m

    def avg_beta(
            self,
            data: List[Tuple[float, List[float], List[float]]]
    ) -> List[Tuple[float, float]]:

        res = compute_avg_beta(data)
        if not res:
            raise ValueError("Нет достаточных данных для расчёта β.")
        return res

    def set_voltage(self, voltage: float):
        packet = self.voltage_builder.build_float(voltage)
        self.stand.send_bytes(packet)
