import struct
from stand_reader import ser


def parse_float(data_bytes):
    return struct.unpack('<f', data_bytes)[0]


class StandController:
    def __init__(self):
        self.ser = ser

    def get_voltage_current(self):
        try:
            # Запрос Uвых и Iвых
            self.ser.write(bytes.fromhex("14 10 00 02 01 02 05 00"))
            response1 = self.ser.read(32)

            # Запрос Uвх
            self.ser.write(bytes.fromhex("20 10 00 02 02 04 34 00"))
            response2 = self.ser.read(32)
            #print(parse_float(response2[12:16]))


            #self.ser.write(bytes.fromhex("1f 10 00 02 02 04 0b 00"))
            #response3 = self.ser.read(32)
            #print(parse_float(response3[6:10]))

            if len(response1) >= 18:
                u_vyk = parse_float(response1[6:10])
                i_vyk = parse_float(response1[12:16])
            else:
                u_vyk = i_vyk = 0.0

            if len(response2) >= 18:
                u_vkh = parse_float(response2[12:16])
            else:
                u_vkh = 0.0

            return u_vkh, abs(u_vyk), i_vyk * 1000  # в мА

        except Exception as e:
            raise RuntimeError(f"Ошибка при работе с лабораторным стендом: {str(e)}")