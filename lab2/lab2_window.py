from PyQt6.QtGui import QBrush, QColor
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidgetItem, QMessageBox
)

from lab2.controller_lab2 import Lab2Controller
from lab2.const_lab2 import *
from utils.excel_timer_helper import update_timer_label, export_tables_to_excel
from utils.tables.paste_table_widget import PasteTableWidget
from formulas.formulas_window import FormulasWindow

from PyQt6.QtCore import QTimer
from datetime import datetime

import matplotlib.pyplot as plt

from utils.tables.table_validator import NumberDelegate
from utils.tables.voltage_control import VoltageControl


class Lab2Window(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Лабораторная работа №2. Исследование стабилитрона")
        self.controller = Lab2Controller()
        self.start_time = datetime.now()
        self.row = 0

        self.table_vah = PasteTableWidget(TABLE_ROW_COUNT, TABLE_COLUMN_COUNT)
        self.table_vah.setHorizontalHeaderLabels(["Uвх, В", "Uвых, В", "Iвых, мА"])
        self.table_vah.setMaximumWidth(TABLE_WIDTH)

        self.table_rd = PasteTableWidget(TABLE_ROW_COUNT, TABLE_RESISTANCE_COLUMN_COUNT)
        self.table_rd.setHorizontalHeaderLabels(["Uвых, В", "Iвых, мА", "rd (ΔU/ΔI), Ом", "rd (nUt/Id), Ом"])
        self.table_rd.setMaximumWidth(TABLE_RESISTANCE_WIDTH)
        self.avg_rd_label = QLabel("Среднее rd: - ")

        delegate = NumberDelegate(self)
        self.table_vah.setItemDelegate(delegate)
        self.table_rd.setItemDelegate(delegate)

        self.button_measure = QPushButton("Снять значение")
        self.button_measure.clicked.connect(self.read_from_stand)

        self.button_plot = QPushButton("Построить ВАХ стабилитрона")
        self.button_plot.clicked.connect(self.plot_vah)

        self.button_calc_rd = QPushButton("Рассчитать динамическое сопротивление")
        self.button_calc_rd.clicked.connect(self.calculate_rd)

        self.button_formulas = QPushButton("Формулы")
        self.button_formulas.clicked.connect(self.show_formulas_window)

        self.button_find_stabilization = QPushButton("Найти начало стабилизации")
        self.button_find_stabilization.clicked.connect(self.find_stabilization_start)

        self.btn_save_all = QPushButton("Сохранить всё в Excel")
        self.btn_save_all.clicked.connect(self.on_save_all)

        self.timer_label = QLabel("Время выполнения работы 0:00:00")

        self.button_exit = QPushButton("Завершить выполнение работы")
        self.button_exit.clicked.connect(self.close)

        vc = VoltageControl(on_submit=self.controller.set_voltage)

        main_layout = QHBoxLayout()
        table_layout = QVBoxLayout()
        side_layout = QVBoxLayout()

        upper_layout = QHBoxLayout()
        vah_layout = QVBoxLayout()
        rd_layout = QVBoxLayout()

        vah_layout.addWidget(QLabel("ВАХ стабилитрона"))
        vah_layout.addWidget(self.table_vah)
        vah_layout.addWidget(self.button_measure)

        rd_layout.addWidget(QLabel("Динамическое сопротивление"))
        rd_layout.addWidget(self.table_rd)

        upper_layout.addLayout(vah_layout, 2)
        upper_layout.addLayout(rd_layout, 1)

        table_layout.addLayout(upper_layout)

        side_layout.addWidget(self.button_plot)
        side_layout.addWidget(self.button_calc_rd)
        side_layout.addWidget(self.button_formulas)
        side_layout.addWidget(self.button_find_stabilization)
        side_layout.addWidget(self.btn_save_all)
        side_layout.addWidget(vc)
        side_layout.addStretch()
        side_layout.addWidget(self.timer_label)
        side_layout.addWidget(self.avg_rd_label)
        side_layout.addWidget(self.button_exit)

        main_layout.addLayout(table_layout, 3)
        main_layout.addLayout(side_layout, 1)
        self.setLayout(main_layout)

        timer = QTimer(self)
        timer.timeout.connect(lambda: update_timer_label(self.start_time, self.timer_label))
        timer.start(1000)

    def read_from_stand(self):
        try:
            m = self.controller.measure()

            if self.row < self.table_vah.rowCount():
                self.table_vah.setItem(self.row, COLUMN_NUMBER_ONE, QTableWidgetItem(f"{m.u_in:.3f}"))
                self.table_vah.setItem(self.row, COLUMN_NUMBER_TWO, QTableWidgetItem(f"{m.u_out:.3f}"))
                self.table_vah.setItem(self.row, COLUMN_NUMBER_THREE, QTableWidgetItem(f"{m.i_out_mA:.3f}"))
                self.row += 1

        except RuntimeError as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при считывании данных со стенда: {e}")

    def plot_vah(self):
        u_vals = []
        i_vals = []

        for row in range(self.table_vah.rowCount()):
            try:
                u_item = self.table_vah.item(row, COLUMN_NUMBER_TWO)
                i_item = self.table_vah.item(row, COLUMN_NUMBER_THREE)
                if u_item and i_item:
                    u = float(u_item.text())
                    i = float(i_item.text())
                    u_vals.append(u)
                    i_vals.append(i)
            except ValueError:
                continue

        if len(u_vals) < MIN_POINTS_TO_SHOW_PLOT:
            QMessageBox.information(self, "Ошибка", f"Недостаточно данных для построения графика. Минимум точек: "
                                                    f"{MIN_POINTS_TO_SHOW_PLOT}")
            return

        plt.figure(figsize=(8, 6))
        plt.plot(u_vals, i_vals, marker='o', linestyle='-', label='ВАХ стабилитрона')
        plt.xlabel("Uвых, В")
        plt.ylabel("Iвых, мА")
        plt.title("ВАХ стабилитрона")
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        plt.show()

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

    def calculate_rd(self):

        U, I_mA = self.get_ui_data_from_table(self.table_vah)

        try:
            rows = self.controller.compute_rd_from_lists(
                u_list=U,
                i_mA_list=I_mA,
                n=STAB_N,
                Ut=U_T
            )
        except ValueError as e:
            QMessageBox.information(self, "Ошибка", str(e))
            return

        self.table_rd.clearContents()
        self.table_rd.setRowCount(len(rows))
        for r, (u0, i0, rd_d, rd_t) in enumerate(rows):
            self.table_rd.setItem(r, COLUMN_NUMBER_ONE, QTableWidgetItem(f"{u0:.3f}"))
            self.table_rd.setItem(r, COLUMN_NUMBER_TWO, QTableWidgetItem(f"{i0:.3f}"))
            self.table_rd.setItem(r, COLUMN_NUMBER_THREE, QTableWidgetItem(f"{rd_d:.3f}"))
            self.table_rd.setItem(r, COLUMN_NUMBER_FOUR, QTableWidgetItem(f"{rd_t:.3f}"))

    def find_stabilization_start(self):
        u_vals, i_vals = self.get_ui_data_from_table(self.table_vah)

        try:
            idx, u_arr, i_arr = self.controller.compute_stabilization_from_lists(
                u_list=u_vals,
                i_list=i_vals,
                min_rd=MIN_RD_CONDITION
            )
        except ValueError as e:
            QMessageBox.information(self, "Ошибка", str(e))
            return

        if idx < 0:
            QMessageBox.information(self, "Ошибка", "Участок стабилизации не найден")
            return

        self.plot_stabilization_region(u_arr, i_arr, idx)

        rows = self.controller.compute_rd_from_lists(
            u_list=u_vals[idx:],
            i_mA_list=i_vals[idx:],
            n=STAB_N,
            Ut=U_T
        )
        rd_avg = self.controller.average_rd(rows)

        self.avg_rd_label.setText(f"Среднее rd на участке стабилизации: {rd_avg:.3f} Ω")

        highlight_brush = QBrush(QColor(255, 255, 0))
        for col in range(self.table_rd.columnCount()):
            self.table_rd.item(idx, col).setBackground(highlight_brush)

        self.table_rd.scrollToItem(self.table_rd.item(idx, 0))

    def plot_stabilization_region(self, u_vals, i_vals, stab_start_index):

        plt.figure(figsize=(8, 6))
        plt.plot(u_vals, i_vals, 'o-', label="ВАХ стабилитрона")

        u_stab = u_vals[stab_start_index]
        i_stab = i_vals[stab_start_index]
        plt.plot(u_stab, i_stab, 'ro', label=f"Начало стабилизации\nU={u_stab:.2f} В, I={i_stab:.2f} мА")

        u_stab_slice = u_vals[stab_start_index:]
        i_stab_slice = i_vals[stab_start_index:]
        plt.plot(u_stab_slice, i_stab_slice, 'g-', linewidth=2, label="Участок стабилизации")

        plt.xlabel("Uвых, В")
        plt.ylabel("Iвых, мА")
        plt.title("ВАХ стабилитрона с выделением стабилизации")
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        plt.show()

    def show_formulas_window(self):
        self.formulas_window = FormulasWindow(lab_number=2)
        self.formulas_window.show()

    def on_save_all(self):
        tables = {
            "ВАХ": self.table_vah,
            "Rдин": self.table_rd,
        }
        export_tables_to_excel(self, tables)
