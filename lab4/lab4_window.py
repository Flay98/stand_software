import numpy as np
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, \
    QMessageBox
from matplotlib import pyplot as plt
from lab4.const_lab4 import *
from lab4.controller_lab4 import Lab4Controller
from utils.excel_timer_helper import update_timer_label, export_tables_to_excel

from utils.tables.paste_table_widget import PasteTableWidget
from formulas.formulas_window import FormulasWindow

from PyQt6.QtCore import QTimer
from datetime import datetime

from utils.tables.table_validator import NumberDelegate


class Lab4Window(QWidget):
    def __init__(self):
        super().__init__()
        self.controller = Lab4Controller()
        self.start_time = datetime.now()
        self.setWindowTitle("Лабораторная работа №4. Исследование ВАХ стабилизатора")
        self.row = 0
        self.current_output_col = 0

        self.table_amplitude = PasteTableWidget(TABLE_AMPLITUDE_ROW_COUNT, TABLE_AMPLITUDE_COLUMN_COUNT)
        self.table_amplitude.setHorizontalHeaderLabels(["Uпит, В", "Uнагр, В", "Iнагр, мА"])
        self.button_read_amplitude = QPushButton("Снять значение (амплитудная)")
        self.button_read_amplitude.clicked.connect(self.read_from_stand_table_amplitude)

        self.table_output = PasteTableWidget(TABLE_OUTPUT_ROW_COUNT, TABLE_OUTPUT_COLUMN_COUNT)
        self.table_output.setVerticalHeaderLabels([
            "Rн, Ом", "Uпит, В", "Iпит, мА", "Uнагр, В", "Iнагр, мА",
            "Pвх, Вт", "Pн, Вт", "КПД", "Iст, мА"
        ])
        self.table_output.setHorizontalHeaderLabels(["100", "200", "300", "400", "600", "800", "1000", "inf"])

        self.table_output.horizontalHeader().hide()
        self.button_read_output = QPushButton("Снять значение (выходная)")
        self.button_read_output.clicked.connect(self.read_from_stand_table_output)

        for col in range(self.table_output.columnCount()):
            text = self.table_output.horizontalHeaderItem(col).text()
            item = QTableWidgetItem(text)
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table_output.setItem(ROW_NUMBER_ONE, col, item)

        delegate = NumberDelegate(self)
        self.table_amplitude.setItemDelegate(delegate)
        self.table_output.setItemDelegate(delegate)

        self.button_plot_vh = QPushButton("Зависимость напряжения на нагрузке от напряжения питания")
        self.button_plot_vh.clicked.connect(self.show_plot_vh)

        self.button_k_st = QPushButton("Найти коэффициент стабилизации на участке стабилизации")
        self.button_k_st.clicked.connect(self.calculate_stabilization_coefficient)

        self.button_p_vh = QPushButton("Посчитать входную мощность")
        self.button_p_vh.clicked.connect(self.on_calc_input_power)

        self.button_p_vyh = QPushButton("Посчитать выходную мощность")
        self.button_p_vyh.clicked.connect(self.on_calc_output_power)

        self.button_calc_efficiency = QPushButton("Посчитать КПД")
        self.button_calc_efficiency.clicked.connect(self.on_calc_efficiency)

        self.button_i_st = QPushButton("Посчитать ток стабилизатора")
        self.button_i_st.clicked.connect(self.on_calc_stabilization_current)

        self.button_plot = QPushButton("Построить график выходной характеристики")
        self.button_plot.clicked.connect(self.show_plot_vyh)

        self.button_formulas = QPushButton("Формулы")
        self.button_formulas.clicked.connect(self.show_formulas)

        self.btn_save_all = QPushButton("Сохранить всё в Excel")
        self.btn_save_all.clicked.connect(self.on_save_all)

        self.timer_label = QLabel("Время выполнения работы 0:00:00")

        self.button_exit = QPushButton("Завершить работу")
        self.button_exit.clicked.connect(self.close)

        layout_main = QHBoxLayout()
        layout_tables = QVBoxLayout()
        layout_side = QVBoxLayout()

        layout_tables.addWidget(QLabel("Амплитудная характеристика стабилизатора"))
        layout_tables.addWidget(self.table_amplitude)
        layout_tables.addWidget(self.button_read_amplitude)

        layout_tables.addSpacing(20)
        layout_tables.addWidget(QLabel("Выходная характеристика стабилизатора"))
        layout_tables.addWidget(self.table_output)
        layout_tables.addWidget(self.button_read_output)

        layout_side.addWidget(self.button_plot_vh)
        layout_side.addWidget(self.button_k_st)
        layout_side.addWidget(self.button_p_vh)
        layout_side.addWidget(self.button_p_vyh)
        layout_side.addWidget(self.button_calc_efficiency)
        layout_side.addWidget(self.button_i_st)
        layout_side.addWidget(self.button_plot)
        layout_side.addWidget(self.button_formulas)
        layout_side.addWidget(self.btn_save_all)

        layout_side.addStretch()

        layout_side.addWidget(self.timer_label)
        layout_side.addWidget(self.button_exit)

        layout_main.addLayout(layout_tables, 3)
        layout_main.addLayout(layout_side, 1)
        self.setLayout(layout_main)

        timer = QTimer(self)
        timer.timeout.connect(lambda: update_timer_label(self.start_time, self.timer_label))
        timer.start(1000)

    def _read_two_columns(self, table: QTableWidget, col_x: int, col_y: int):
        x_vals, y_vals = [], []
        for r in range(table.rowCount()):
            item_x = table.item(r, col_x)
            item_y = table.item(r, col_y)
            if not item_x or not item_y:
                continue
            try:
                x = float(item_x.text())
                y = float(item_y.text())
            except ValueError:
                continue
            x_vals.append(x)
            y_vals.append(y)
        return x_vals, y_vals

    def show_plot_vh(self):
        u_pit_vals, u_load_vals = self._read_two_columns(
            self.table_amplitude,
            COLUMN_NUMBER_ONE,
            COLUMN_NUMBER_TWO
        )
        if len(u_pit_vals) < MIN_POINTS_TO_SHOW_PLOT:
            QMessageBox.information(
                self, "Ошибка",
                f"Недостаточно данных для построения графика (минимум {MIN_POINTS_TO_SHOW_PLOT} точек)"
            )
            return

        plt.figure(figsize=(8, 6))
        plt.plot(u_pit_vals, u_load_vals, 'o-')
        plt.xlabel("Uпит, В")
        plt.ylabel("Uнагр, В")
        plt.title("Зависимость Uнагрузки от Uпитания")
        plt.grid(True)
        plt.tight_layout()
        plt.show()

    def calculate_stabilization_coefficient(self):

        u_pit, u_load = self._read_two_columns(
            self.table_amplitude,
            COLUMN_NUMBER_ONE,
            COLUMN_NUMBER_TWO
        )

        try:
            start, k_vals, k_avg = self.controller.comp_stabilization_coefficient(
                u_pit=u_pit,
                u_load=u_load
            )
        except ValueError as e:
            QMessageBox.information(self, "Ошибка", str(e))
            return

        msg = (
            f"Начало стабилизации: строка {start}\n"
            f"Среднее относительное Kст = {k_avg:.2f}"
        )
        QMessageBox.information(self, "Коэффициент стабилизации", msg)

    def read_and_append_row(self, table, row_index):
        try:
            m = self.controller.measure()

            if row_index < table.rowCount():
                table.setItem(row_index, COLUMN_NUMBER_ONE, QTableWidgetItem(f"{m.u_in:.3f}"))
                table.setItem(row_index, COLUMN_NUMBER_TWO, QTableWidgetItem(f"{m.u_out:.3f}"))
                table.setItem(row_index, COLUMN_NUMBER_THREE, QTableWidgetItem(f"{m.i_out_mA:.3f}"))
                row_index += 1

        except RuntimeError as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при чтении со стенда: {e}")

        return row_index

    def read_and_append_column(self, table: QTableWidget, col_index: int):
        try:
            m = self.controller.measure()

            if col_index < table.columnCount():
                table.setItem(ROW_NUMBER_TWO, col_index, QTableWidgetItem(f"{m.u_in:.3f}"))
                table.setItem(ROW_NUMBER_FOUR, col_index, QTableWidgetItem(f"{m.u_out:.3f}"))
                table.setItem(ROW_NUMBER_FIVE, col_index, QTableWidgetItem(f"{m.i_out_mA:.3f}"))
                col_index += 1

        except RuntimeError as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при чтении со стенда: {e}")

        return col_index

    def read_from_stand_table_output(self):
        self.current_output_col = self.read_and_append_column(self.table_output, self.current_output_col)

    def read_from_stand_table_amplitude(self):
        self.row = self.read_and_append_row(self.table_amplitude, self.row)

    def _extract_output_table(self):
        result = []
        for col in range(self.table_output.columnCount()):
            try:
                u_pit = float(self.table_output.item(ROW_NUMBER_TWO, col).text())
                i_pit = float(self.table_output.item(ROW_NUMBER_THREE, col).text())
                u_load = float(self.table_output.item(ROW_NUMBER_FOUR, col).text())
                i_load = float(self.table_output.item(ROW_NUMBER_FIVE, col).text())
            except Exception:
                continue
            result.append((col, u_pit, i_pit, u_load, i_load))
        return result

    def on_calc_input_power(self):
        data = self._extract_output_table()
        try:
            pin, _, _, _ = self.controller.comp_stabilizer_metrics(data)
        except ValueError as e:
            QMessageBox.information(self, "Ошибка", str(e))
            return
        for col, val in pin:
            self.table_output.setItem(5, col, QTableWidgetItem(f"{val:.3f}"))

    def on_calc_output_power(self):
        data = self._extract_output_table()
        try:
            _, pout, _, _ = self.controller.comp_stabilizer_metrics(data)
        except ValueError as e:
            QMessageBox.information(self, "Ошибка", str(e))
            return
        for col, val in pout:
            self.table_output.setItem(6, col, QTableWidgetItem(f"{val:.3f}"))

    def on_calc_efficiency(self):
        data = self._extract_output_table()
        try:
            _, _, eta, _ = self.controller.comp_stabilizer_metrics(data)
        except ValueError as e:
            QMessageBox.information(self, "Ошибка", str(e))
            return
        for col, val in eta:
            self.table_output.setItem(7, col, QTableWidgetItem(f"{val:.3f}"))

    def on_calc_stabilization_current(self):
        data = self._extract_output_table()
        try:
            _, _, _, ist = self.controller.comp_stabilizer_metrics(data)
        except ValueError as e:
            QMessageBox.information(self, "Ошибка", str(e))
            return
        for col, val in ist:
            self.table_output.setItem(8, col, QTableWidgetItem(f"{val:.3f}"))

    def show_plot_vyh(self):
        Rn = []
        U_nagr = []
        I_nagr = []

        cols = self.table_output.columnCount()
        for col in range(cols):
            text = self.table_output.horizontalHeaderItem(col).text()
            if text == "inf":
                r = np.inf
            else:
                try:
                    r = float(text)
                except ValueError:
                    continue
            Rn.append(r)

            item_u = self.table_output.item(ROW_NUMBER_FOUR, col)
            U_nagr.append(float(item_u.text()) if item_u else np.nan)

            item_i = self.table_output.item(ROW_NUMBER_FIVE, col)
            I_nagr.append(float(item_i.text()) if item_i else np.nan)

        Rn = np.array(Rn)
        U_nagr = np.array(U_nagr)
        I_nagr = np.array(I_nagr)

        mask1 = (~np.isnan(U_nagr)) & (~np.isnan(Rn)) & (Rn != np.inf)
        mask2 = (~np.isnan(U_nagr)) & (~np.isnan(I_nagr))

        if mask1.sum() >= MIN_POINTS_TO_SHOW_PLOT:
            plt.figure(figsize=(8, 5))
            plt.plot(Rn[mask1], U_nagr[mask1], 'o-', label="Uнаг \u2192 Rн")
            plt.xlabel("Rн, Ом")
            plt.ylabel("Uнагр, В")
            plt.title("Зависимость напряжения нагрузки от сопротивления")
            plt.grid(True)
            plt.tight_layout()
            plt.show()
        else:
            QMessageBox.information(self, "Ошибка", "Недостаточно данных для графика Uнагр = f(Rн)")

        if mask2.sum() >= MIN_POINTS_TO_SHOW_PLOT:
            plt.figure(figsize=(8, 5))
            plt.plot(I_nagr[mask2], U_nagr[mask2], 's-', label="Uнаг \u2192 Iнаг")
            plt.xlabel("Iнагр, мА")
            plt.ylabel("Uнагр, В")
            plt.title("Зависимость напряжения нагрузки от тока нагрузки")
            plt.grid(True)
            plt.tight_layout()
            plt.show()
        else:
            QMessageBox.information(self, "Ошибка", "Недостаточно данных для графика Uнагр = f(Iнагр)")

    def show_formulas(self):
        self.formulas_window = FormulasWindow(lab_number=4)
        self.formulas_window.show()

    def on_save_all(self):
        tables = {
            "Амплитудная х-ка": self.table_amplitude,
            "Выходная х-ка": self.table_output,
        }
        export_tables_to_excel(self, tables)
