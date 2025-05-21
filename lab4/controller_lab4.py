from typing import List, Tuple

from lab4.calculations_lab4 import compute_stabilization_coefficient, compute_stabilizer_metrics
from lab4.const_lab4 import MIN_POINTS_TO_CALC_STAB, STAB_THRESHOLD
from utils.packet_builder import PacketBuilder
from utils.stand_controller import StandController
from utils.data.measurement import Measurement


class Lab4Controller:
    def __init__(self):
        self.stand = StandController()
        self.vh: List[Measurement] = []

        self.voltage_builder = PacketBuilder(bytes([0x20, 0x50, 0x00, 0x01, 0x02, 0x01]))

    def measure(self) -> Measurement:
        m = self.stand.get_voltage_current()
        self.vh.append(m)
        return m

    def comp_stabilization_coefficient(
            self,
            u_pit: List[float],
            u_load: List[float]
    ) -> Tuple[int, List[float], float]:
        return compute_stabilization_coefficient(
            u_pit_list=u_pit,
            u_load_list=u_load,
            min_points=MIN_POINTS_TO_CALC_STAB,
            threshold=STAB_THRESHOLD
        )

    def comp_stabilizer_metrics(
            self,
            table_data: List[Tuple[int, float, float, float, float]]
    ) -> Tuple[
        List[Tuple[int, float]],
        List[Tuple[int, float]],
        List[Tuple[int, float]],
        List[Tuple[int, float]]
    ]:
        return compute_stabilizer_metrics(table_data)

    def set_voltage(self, voltage: float):
        packet = self.voltage_builder.build_float(voltage)
        self.stand.send_bytes(packet)
