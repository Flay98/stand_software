from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QTableWidgetItem, QTableWidget, \
    QMessageBox
from matplotlib import pyplot as plt

from formulas.formulas_window import FormulasWindow
from lab1.controller_lab1 import Lab1Controller
from utils.excel_timer_helper import update_timer_label, export_tables_to_excel
from utils.paste_table_widget import PasteTableWidget
from lab1.const_lab1 import *

from PyQt6.QtCore import QTimer
from datetime import datetime


class Lab1Window(QWidget):
    def __init__(self):
        super().__init__()
        self.controller = Lab1Controller()
        self.start_time = datetime.now()
        self.setWindowTitle("Лабораторная работа №1. Исследование ВАХ диодов")

        self.row = 0
        self.row_Schottky = 0

        self.table_si = PasteTableWidget(TABLE_ROW_COUNT, TABLE_COLUMN_COUNT)
        self.table_si.setHorizontalHeaderLabels(["Uвх, В", "Uвых, В", "Iвых, мА"])
        self.table_si.setMaximumWidth(TABLE_WIDTH)

        self.table_Schottky = PasteTableWidget(TABLE_ROW_COUNT, TABLE_COLUMN_COUNT)
        self.table_Schottky.setHorizontalHeaderLabels(["Uвх, В", "Uвых, В", "Iвых, мА"])
        self.table_Schottky.setMaximumWidth(TABLE_WIDTH)

        self.table_dSi = PasteTableWidget(TABLE_ROW_COUNT, TABLE_RESISTANCE_COLUMN_COUNT)
        self.table_dSi.setHorizontalHeaderLabels(["Uвых, В", "Iвых, мА", "rd (ΔU/ΔI), Ом", "rd (nUt/Id), Ом"])
        self.table_dSi.setMaximumWidth(TABLE_RESISTANCE_WIDTH)

        self.table_dSchottky = PasteTableWidget(TABLE_ROW_COUNT, TABLE_RESISTANCE_COLUMN_COUNT)
        self.table_dSchottky.setHorizontalHeaderLabels(["Uвых, В", "Iвых, мА", "rd (ΔU/ΔI), Ом", "rd (nUt/Id), Ом"])
        self.table_dSchottky.setMaximumWidth(TABLE_RESISTANCE_WIDTH)

        self.button_measure_si = QPushButton("Снять значение")
        self.button_measure_si.clicked.connect(self.read_from_stand)

        self.button_measure_Schottky = QPushButton("Снять значение")
        self.button_measure_Schottky.clicked.connect(self.read_from_stand_schottky)

        self.button_compare_graph = QPushButton("График сравнения ВАХ диодов")
        self.button_compare_graph.clicked.connect(self.build_compare_graph)

        self.button_Shockley_Si_graph = QPushButton("Подбор параметров уравнения Шокли по экспериментальным данным для "
                                                    "кремниевого диода")
        self.button_Shockley_Si_graph.clicked.connect(
            lambda: self.on_shockley(self.table_si))

        self.button_Shockley_Schottky_graph = QPushButton(
            "Подбор параметров уравнения Шокли по экспериментальным данным для "
            "германиевого диода")
        self.button_Shockley_Schottky_graph.clicked.connect(
            lambda: self.on_shockley(self.table_Schottky))

        self.button_calc_dSi = QPushButton("Расчёт динамического сопротивления кремниевого диода")
        self.button_calc_dSi.clicked.connect(self.on_calc_rd_si)

        self.button_calc_dSchottky = QPushButton("Расчёт динамического сопротивления диода Шоттки")
        self.button_calc_dSchottky.clicked.connect(self.on_calc_rd_sch)

        self.button_compare_Si_theor_graph = QPushButton("Сравнение экспериментальной и теоретической ВАХ для "
                                                         "кремниевого диода")
        self.button_compare_Si_theor_graph.clicked.connect(self.on_compare_exp_theor)

        self.button_calc_dSi_theor = QPushButton("Расчёт теоретического динамического сопротивления Si")
        self.button_calc_dSi_theor.clicked.connect(self.on_calc_theoretical_rd)

        self.button_formulas = QPushButton("Формулы")
        self.button_formulas.clicked.connect(self.show_formulas_window)

        self.btn_save_all = QPushButton("Сохранить всё в Excel")
        self.btn_save_all.clicked.connect(self.on_save_all)

        self.timer_label = QLabel("Время выполнения работы 00:00:00")

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

        schottky_layout = QHBoxLayout()
        schottky_left = QVBoxLayout()
        schottky_right = QVBoxLayout()

        schottky_left.addWidget(QLabel("ВАХ диода Шоттки"))
        schottky_left.addWidget(self.table_Schottky)
        schottky_left.addWidget(self.button_measure_Schottky)

        schottky_right.addWidget(QLabel("Динамическое сопротивление диода Шоттки"))
        schottky_right.addWidget(self.table_dSchottky)

        schottky_layout.addLayout(schottky_left, 2)
        schottky_layout.addLayout(schottky_right, 1)

        table_layout.addLayout(si_layout)
        table_layout.addLayout(schottky_layout)

        side_layout.addWidget(self.button_compare_graph)
        side_layout.addWidget(self.button_Shockley_Si_graph)
        side_layout.addWidget(self.button_Shockley_Schottky_graph)
        side_layout.addWidget(self.button_calc_dSi)
        side_layout.addWidget(self.button_calc_dSchottky)
        side_layout.addWidget(self.button_compare_Si_theor_graph)
        side_layout.addWidget(self.button_calc_dSi_theor)
        side_layout.addWidget(self.button_formulas)
        side_layout.addWidget(self.btn_save_all)

        side_layout.addStretch()
        side_layout.addWidget(self.timer_label)
        side_layout.addWidget(self.button_exit)

        main_layout.addLayout(table_layout, 3)
        main_layout.addLayout(side_layout, 1)

        self.setLayout(main_layout)

        timer = QTimer(self)
        timer.timeout.connect(lambda: update_timer_label(self.start_time, self.timer_label))
        timer.start(1000)

    def on_compare_exp_theor(self):
        try:
            U, I_exp, U_th, I_th, label = self.controller.compute_exp_theor_vah(
                u=self.get_ui_data_from_table(self.table_si)[0],
                i_mA=self.get_ui_data_from_table(self.table_si)[1],
                Is=I_S_SI,
                n=SI_N,
                Rs=R_S_SI,
                Ut=U_T
            )
        except ValueError as e:
            QMessageBox.information(self, "Ошибка", str(e))
            return

        plt.figure(figsize=(10, 6))
        plt.plot(U, I_exp, 'o-', label='Экспериментальная ВАХ')
        plt.plot(U_th, I_th, 'r-', label=f'Теоретическая ВАХ\n{label}')
        plt.xlabel("U (В)")
        plt.ylabel("I (мА)")
        plt.title("Сравнение экспериментальной и теоретической ВАХ")
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        plt.show()

    def on_calc_rd_si(self):
        try:
            U, I_mA = self.get_ui_data_from_table(self.table_si)
            rows = self.controller.calculate_dynamic_resistance(U, I_mA, n_value=1.84)
        except ValueError as e:
            QMessageBox.information(self, "Ошибка", str(e))
            return

        self._populate_rd_table(self.table_dSi, rows)

    def on_calc_rd_sch(self):
        try:
            U, I_mA = self.get_ui_data_from_table(self.table_Schottky)
            rows = self.controller.calculate_dynamic_resistance(U, I_mA, n_value=1.15)
        except ValueError as e:
            QMessageBox.information(self, "Ошибка", str(e))
            return

        self._populate_rd_table(self.table_dSchottky, rows)

    def _populate_rd_table(self, table, rows):
        table.clearContents()
        table.setRowCount(len(rows))
        for r, (u, i, rd_d, rd_t) in enumerate(rows):
            for c, val in enumerate((u, i, rd_d, rd_t)):
                table.setItem(r, c, QTableWidgetItem(f"{val:.3f}"))

    def read_and_append_row(self, table, target, row_index):
        try:
            m = self.controller.add_measurement(target)
            if row_index < table.rowCount():
                table.setItem(row_index, COLUMN_NUMBER_ONE, QTableWidgetItem(f"{m[0]:.1f}"))
                table.setItem(row_index, COLUMN_NUMBER_TWO, QTableWidgetItem(f"{m[1]:.3f}"))
                table.setItem(row_index, COLUMN_NUMBER_THREE, QTableWidgetItem(f"{m[2]:.3f}"))
                row_index += 1

        except RuntimeError as e:
            print(str(e))

        return row_index

    def read_from_stand(self):
        self.row = self.read_and_append_row(self.table_si, 'si', self.row)

    def read_from_stand_schottky(self):
        self.row_Schottky = self.read_and_append_row(self.table_Schottky, 'sch', self.row_Schottky)

    def get_ui_data_from_table(self, table):
        U = []
        I = []
        for row in range(table.rowCount()):
            try:
                u_val = table.item(row, COLUMN_NUMBER_TWO)
                i_val = table.item(row, COLUMN_NUMBER_THREE)
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
        u_Schottky, i_Schottky = self.get_ui_data_from_table(self.table_Schottky)

        plt.figure(figsize=(10, 6))
        plt.plot(u_si, i_si, marker='o', linestyle='-', label="Кремниевый диод (Si)")
        plt.plot(u_Schottky, i_Schottky, marker='s', linestyle='-', label="Германиевый диод (Ge)")

        plt.xlabel("Напряжение на диоде, В", fontsize=12)
        plt.ylabel("Ток через диод, мА", fontsize=12)
        plt.title("Сравнение ВАХ кремниевого и германиевого диодов", fontsize=14)
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        plt.show()

    def on_calc_theoretical_rd(self):
        U, _ = self.get_ui_data_from_table(self.table_si)
        try:
            rows = self.controller.compute_theoretical_rd(
                u_list=U,
                Is=I_S_SI,
                n=SI_N,
                Rs=R_S_SI,
                Ut=U_T
            )
        except ValueError as e:
            QMessageBox.information(self, "Ошибка", str(e))
            return

        dialog = QWidget()
        dialog.setWindowTitle("Теоретическое динамическое сопротивление (Si)")
        dialog.resize(550, 400)

        layout = QVBoxLayout(dialog)
        table = QTableWidget()
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["U, В", "I, мА", "rd (ΔU/ΔI), Ом", "rd (nUt/Id), Ом"])
        table.setRowCount(len(rows))

        for r, (u0, i0, rd_d, rd_t) in enumerate(rows):
            for c, val in enumerate((u0, i0, rd_d, rd_t)):
                item = QTableWidgetItem(f"{val:.3f}")
                table.setItem(r, c, item)

        layout.addWidget(QLabel("Теоретический расчет rd на основе уравнения Шокли"))
        layout.addWidget(table)

        dialog.setLayout(layout)
        dialog.show()

        self.theor_dialog = dialog

    def on_shockley(self, table):

        U, I_mA = self.get_ui_data_from_table(table)

        try:
            U_th, I_th, Is_fit, n_fit = self.controller.get_shockley_data(
                u_list=U,
                i_list=I_mA,
                Ut=U_T
            )
        except ValueError as e:
            QMessageBox.information(self, "Ошибка", str(e))
            return

        plt.figure(figsize=(10, 6))
        plt.plot(U, I_mA, 'o', label='Экспериментальные данные')
        plt.plot(U_th, I_th, '-', label=f'Теоретическая кривая\nIs={Is_fit:.2e} A, n={n_fit:.2f}')
        plt.xlabel("Напряжение на диоде, В")
        plt.ylabel("Ток через диод, мА")
        plt.title("Аппроксимация уравнения Шокли")
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        plt.show()

    def show_formulas_window(self):
        self.formulas_window = FormulasWindow(lab_number=1)
        self.formulas_window.show()

    def on_save_all(self):
        tables = {
            "ВАХ кремниевого диода": self.table_si,
            "ВАХ диода Шоттки": self.table_Schottky,
            "Rдин кремниевого диода": self.table_dSi,
            "Rдин диода Шоттки": self.table_dSchottky,
        }
        export_tables_to_excel(self, tables)


