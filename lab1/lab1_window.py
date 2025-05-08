import numpy as np
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QTableWidgetItem, QTableWidget
from matplotlib import pyplot as plt
from scipy.optimize import curve_fit, fsolve

from formulas_window import FormulasWindow
from paste_table_widget import PasteTableWidget
from stand_controller import StandController
import struct


def parse_float(data_bytes):
    return struct.unpack('<f', data_bytes)[0]


class Lab1Window(QWidget):
    def __init__(self):
        super().__init__()
        self.controller = StandController()
        self.setWindowTitle("Лабораторная работа №1. Исследование ВАХ диодов")

        self.row = 0
        self.row_ge = 0

        self.table_si = PasteTableWidget(36, 3)
        self.table_si.setHorizontalHeaderLabels(["Uвх, В", "Uвых, В", "Iвых, мА"])
        self.table_si.setMaximumWidth(350)

        self.table_ge = PasteTableWidget(36, 3)
        self.table_ge.setHorizontalHeaderLabels(["Uвх, В", "Uвых, В", "Iвых, мА"])
        self.table_ge.setMaximumWidth(350)

        self.table_dSi = PasteTableWidget(36, 4)
        self.table_dSi.setHorizontalHeaderLabels(["Uвых, В", "Iвых, мА", "rd (ΔU/ΔI), Ом", "rd (nUt/Id), Ом"])
        self.table_dSi.setMaximumWidth(500)

        self.table_dSchottky = PasteTableWidget(36, 4)
        self.table_dSchottky.setHorizontalHeaderLabels(["Uвых, В", "Iвых, мА", "rd (ΔU/ΔI), Ом", "rd (nUt/Id), Ом"])
        self.table_dSchottky.setMaximumWidth(500)

        self.button_measure_si = QPushButton("Снять значение")
        self.button_measure_si.clicked.connect(self.read_from_stand)

        self.button_measure_ge = QPushButton("Снять значение")
        self.button_measure_ge.clicked.connect(self.read_from_stand_ge)

        self.button_compare_graph = QPushButton("График сравнения ВАХ диодов")
        self.button_compare_graph.clicked.connect(self.build_compare_graph)

        self.button_Shockley_Si_graph = QPushButton("Подбор параметров уравнения Шокли по экспериментальным данным для "
                                                    "кремниевого диода")
        self.button_Shockley_Si_graph.clicked.connect(lambda: self.shockley_fit(self.table_si, "кремниевого диода"))

        self.button_Shockley_Ge_graph = QPushButton("Подбор параметров уравнения Шокли по экспериментальным данным для "
                                                    "германиевого диода")
        self.button_Shockley_Ge_graph.clicked.connect(lambda: self.shockley_fit(self.table_ge, "Диода Шоттки"))

        self.button_calc_dSi = QPushButton("Расчёт динамического сопротивления кремниевого диода")
        self.button_calc_dSi.clicked.connect(
            lambda: self.calculate_dynamic_resistance(self.table_si, self.table_dSi, n_value=1.84)
        )

        self.button_calc_dGe = QPushButton("Расчёт динамического сопротивления диода Шоттки")
        self.button_calc_dGe.clicked.connect(
            lambda: self.calculate_dynamic_resistance(self.table_ge, self.table_dSchottky, n_value=1.15)
        )

        self.button_compare_Si_theor_graph = QPushButton("Сравнение экспериментальной и теоретической ВАХ для "
                                                         "кремниевого диода")
        self.button_compare_Si_theor_graph.clicked.connect(
            lambda: self.compare_exp_theor_vah(
                table=self.table_si,
                Is=3.2e-8,
                n=2,
                Rs=0.042,
                diode_name="кремниевого диода"
            )
        )
        self.button_calc_dSi_theor = QPushButton("Расчёт теоретического динамического сопротивления Si")
        self.button_calc_dSi_theor.clicked.connect(self.show_theoretical_rd_for_si)
        self.button_formulas = QPushButton("Формулы")
        self.button_formulas.clicked.connect(self.show_formulas_window)
        self.button_exit = QPushButton("Завершить выполнение работы")
        self.button_exit.clicked.connect(self.close)

        main_layout = QHBoxLayout()
        table_layout = QVBoxLayout()
        side_layout = QVBoxLayout()

        si_layout = QHBoxLayout()
        si_left = QVBoxLayout()
        si_right = QVBoxLayout()

        si_left.addWidget(QLabel("ВАХ кремниевого диода"))
        si_left.addWidget(self.table_si)
        si_left.addWidget(self.button_measure_si)

        si_right.addWidget(QLabel("Динамическое сопротивление кремниевого диода"))
        si_right.addWidget(self.table_dSi)

        si_layout.addLayout(si_left, 2)
        si_layout.addLayout(si_right, 1)

        ge_layout = QHBoxLayout()
        ge_left = QVBoxLayout()
        ge_right = QVBoxLayout()

        ge_left.addWidget(QLabel("ВАХ диода Шоттки"))
        ge_left.addWidget(self.table_ge)
        ge_left.addWidget(self.button_measure_ge)

        ge_right.addWidget(QLabel("Динамическое сопротивление диода Шоттки"))
        ge_right.addWidget(self.table_dSchottky)

        ge_layout.addLayout(ge_left, 2)
        ge_layout.addLayout(ge_right, 1)

        table_layout.addLayout(si_layout)
        table_layout.addLayout(ge_layout)

        side_layout.addWidget(self.button_compare_graph)
        side_layout.addWidget(self.button_Shockley_Si_graph)
        side_layout.addWidget(self.button_Shockley_Ge_graph)
        side_layout.addWidget(self.button_calc_dSi)
        side_layout.addWidget(self.button_calc_dGe)
        side_layout.addWidget(self.button_compare_Si_theor_graph)
        side_layout.addWidget(self.button_calc_dSi_theor)
        side_layout.addWidget(self.button_formulas)

        side_layout.addStretch()
        side_layout.addWidget(self.button_exit)

        main_layout.addLayout(table_layout, 3)
        main_layout.addLayout(side_layout, 1)

        self.setLayout(main_layout)

    def compare_exp_theor_vah(self, table: PasteTableWidget, Is: float, n: float, Rs: float = 0.0,
                              diode_name: str = "диода"):
        Ut = 0.0253
        U, I_mA = self.get_ui_data_from_table(table)

        if len(U) == 0 or len(I_mA) == 0:
            print("Недостаточно данных для сравнения")
            return

        U = np.array(U)
        I_exp = np.array(I_mA)

        def shockley_iterative_stable(U_vals, Is, n, Rs, Ut):
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
            return np.array(I_result)

        I_theor = shockley_iterative_stable(U, Is, n, Rs, Ut)

        plt.figure(figsize=(10, 6))
        plt.plot(U, I_exp, 'o-', label='Экспериментальная ВАХ', markersize=4)
        plt.plot(U, I_theor, 'r-', label=f'Теоретическая ВАХ\nIs={Is:.2e} А, n={n:.2f}, Rs={Rs:.3f} Ом')

        plt.xlabel("U (В)", fontsize=12)
        plt.ylabel("I (мА)", fontsize=12)
        plt.title(f"Сравнение экспериментальной и теоретической ВАХ ({diode_name})", fontsize=14)
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        plt.show()

    def calculate_dynamic_resistance(self, source_table: PasteTableWidget, target_table: PasteTableWidget,
                                     n_value: float = 1.5):
        Ut = 0.0253
        U, I_mA = self.get_ui_data_from_table(source_table)
        if len(U) < 2:
            print("Недостаточно точек для расчёта rd")
            return

        target_table.clearContents()
        target_table.setRowCount(len(U) - 1)

        for i in range(len(U) - 1):
            try:
                delta_U = U[i + 1] - U[i]
                delta_I = I_mA[i + 1]*0.001 - I_mA[i]*0.001
                rd_delta = delta_U / delta_I if delta_I != 0 else float('inf')

                I_A = I_mA[i] / 1000
                rd_theor = (n_value * Ut) / I_A if I_A > 0 else float('inf')

            except Exception:
                rd_delta = float('nan')
                rd_theor = float('nan')

            target_table.setItem(i, 0, QTableWidgetItem(f"{U[i]:.3f}"))
            target_table.setItem(i, 1, QTableWidgetItem(f"{I_mA[i]:.3f}"))
            target_table.setItem(i, 2, QTableWidgetItem(f"{rd_delta:.3f}"))
            target_table.setItem(i, 3, QTableWidgetItem(f"{rd_theor:.3f}"))

    def read_and_append_row(self, table, row_index):
        try:
            u_in, u_out, i_out = self.controller.get_voltage_current()
            print(f"Uвх = {u_in:.6f} В, Uвых = {u_out:.6f} В, Iвых = {i_out:.6f} мА")

            if row_index < table.rowCount():
                table.setItem(row_index, 0, QTableWidgetItem(f"{u_in:.6f}"))
                table.setItem(row_index, 1, QTableWidgetItem(f"{u_out:.6f}"))
                table.setItem(row_index, 2, QTableWidgetItem(f"{i_out:.6f}"))
                row_index += 1

        except RuntimeError as e:
            print(str(e))

        return row_index

    def read_from_stand(self):
        self.row = self.read_and_append_row(self.table_si, self.row)

    def read_from_stand_ge(self):
        self.row_ge = self.read_and_append_row(self.table_ge, self.row_ge)

    def get_ui_data_from_table(self, table):
        U = []
        I = []
        for row in range(table.rowCount()):
            try:
                u_val = table.item(row, 1)
                i_val = table.item(row, 2)
                if u_val is not None and i_val is not None:
                    u = float(u_val.text())
                    i = float(i_val.text())
                    U.append(u)
                    I.append(i)
            except ValueError:
                continue
        return U, I

    def build_compare_graph(self):
        u_si, i_si = self.get_ui_data_from_table(self.table_si)
        u_ge, i_ge = self.get_ui_data_from_table(self.table_ge)

        plt.figure(figsize=(10, 6))
        plt.plot(u_si, i_si, marker='o', linestyle='-', label="Кремниевый диод (Si)")
        plt.plot(u_ge, i_ge, marker='s', linestyle='-', label="Германиевый диод (Ge)")

        plt.xlabel("Напряжение на диоде, В", fontsize=12)
        plt.ylabel("Ток через диод, мА", fontsize=12)
        plt.title("Сравнение ВАХ кремниевого и германиевого диодов", fontsize=14)
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        plt.show()

    def show_theoretical_rd_for_si(self):
        U, _ = self.get_ui_data_from_table(self.table_si)
        if len(U) < 2:
            print("Недостаточно данных")
            return

        Is = getattr(self, "si_fit_Is", 3.2e-8)
        n = getattr(self, "si_fit_n", 2.0)
        Rs = 0.042

        self.theor_rd_window = DynamicResistanceTheoreticalWindow(U_array=np.array(U), Is=Is, n=n, Rs=Rs)
        self.theor_rd_window.show()

    def shockley_fit(self, table, diode_name):
        U, I_mA = self.get_ui_data_from_table(table)

        if len(U) == 0 or len(I_mA) == 0:
            print("Недостаточно данных для подбора.")
            return

        U = np.array(U)
        I_mA = np.array(I_mA)
        I = I_mA / 1000

        Ut = 0.0253

        def shockley_eq(U, Is, n):
            return Is * (np.exp(U / (n * Ut)) - 1)

        mask = I > 0
        U_fit = U[mask]
        I_fit = I[mask]

        if len(U_fit) == 0 or len(I_fit) == 0:
            print("Нет валидных данных для аппроксимации.")
            return

        try:
            params, _ = curve_fit(shockley_eq, U_fit, I_fit, p0=[1e-9, 1.5])
            Is_fit, n_fit = params
        except Exception as e:
            print(f"Ошибка подбора параметров: {e}")
            return

        print(f"[{diode_name}] Рассчитанный ток насыщения Is ≈ {Is_fit:.3e} А")
        print(f"[{diode_name}] Рассчитанный коэффициент идеальности n ≈ {n_fit:.2f}")

        U_theor = np.linspace(min(U), max(U), 300)
        I_theor = shockley_eq(U_theor, Is_fit, n_fit) * 1000  # в мА

        plt.figure(figsize=(10, 6))
        plt.plot(U, I_mA, 'o', label='Экспериментальные данные')
        plt.plot(U_theor, I_theor, '-', color='red',
                 label=f'Теоретическая кривая\nIs={Is_fit:.2e} А, n={n_fit:.2f}')
        plt.xlabel("Напряжение на диоде, В")
        plt.ylabel("Ток через диод, мА")
        plt.title(f"Подбор параметров уравнения Шокли для {diode_name}")
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        plt.show()

    def show_formulas_window(self):
        self.formulas_window = FormulasWindow(lab_number=1)
        self.formulas_window.show()


class DynamicResistanceTheoreticalWindow(QWidget):
    def __init__(self, U_array, Is, n, Rs=0.0, Ut=0.0253):
        super().__init__()
        self.setWindowTitle("Теоретическое динамическое сопротивление (Si)")
        self.resize(550, 400)

        I_theor = self.compute_shockley_current(U_array, Is, n, Rs, Ut)

        layout = QVBoxLayout()
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["U, В", "I, мА", "rd (ΔU/ΔI), Ом", "rd (nUt/Id), Ом"])
        self.table.setRowCount(len(U_array) - 1)

        for i in range(len(U_array) - 1):
            U = U_array[i]
            I = I_theor[i]
            U_next = U_array[i + 1]
            I_next = I_theor[i + 1]

            delta_U = U_next - U
            delta_I = I_next*0.001 - I*0.001
            rd_delta = delta_U / delta_I if delta_I != 0 else float('inf')
            rd_theor = (n * Ut) / (I / 1000) if I > 0 else float('inf')

            self.table.setItem(i, 0, QTableWidgetItem(f"{U:.3f}"))
            self.table.setItem(i, 1, QTableWidgetItem(f"{I:.3f}"))
            self.table.setItem(i, 2, QTableWidgetItem(f"{rd_delta:.3f}"))
            self.table.setItem(i, 3, QTableWidgetItem(f"{rd_theor:.3f}"))

        layout.addWidget(QLabel("Теоретический расчет rd на основе уравнения Шокли"))
        layout.addWidget(self.table)
        self.setLayout(layout)

    def compute_shockley_current(self, U_vals, Is, n, Rs, Ut):
        I_result = []
        I_prev = 1e-9
        for U_val in U_vals:
            def current_eq(I):
                exponent = (U_val - I * Rs) / (n * Ut)
                exp_safe = np.exp(np.clip(exponent, -100, 100))
                return Is * (exp_safe - 1) - I

            I_solution = fsolve(current_eq, I_prev)[0]
            I_prev = I_solution
            I_result.append(I_solution * 1000)  # в мА
        return np.array(I_result)

