from datetime import datetime
from typing import Dict, Tuple, List

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidgetItem, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer
from matplotlib import pyplot as plt
from lab9.const_lab9 import *

from formulas.formulas_window import FormulasWindow
from lab9.controller_lab9 import Lab9Controller
from utils.excel_timer_helper import update_timer_label, export_tables_to_excel
from utils.tables.paste_table_widget import PasteTableWidget
from utils.tables.table_validator import NumberDelegate
from utils.tables.voltage_control import VoltageControl


class Lab9Window(QWidget):
    def __init__(self):
        super().__init__()
        self.formulas_window = FormulasWindow(lab_number=9)
        self.controller = Lab9Controller()
        self.setWindowTitle("Исследование статических вольтамперных характеристик полевого транзистора")
        self.start_time = datetime.now()

        headers = ["Uзи, В", "Uси, В"] + ["9", "8", "7", "6", "5", "4", "3", "2", "1", "0.5", "0.2", "0.1"]
        self.table = PasteTableWidget(TABLE_ROW_COUNT, len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setSpan(0, 1, 5, 1)
        hdr = QTableWidgetItem("Ic, мA")
        hdr.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        hdr.setFlags(hdr.flags() & ~Qt.ItemFlag.ItemIsEditable)
        self.table.setItem(0, 1, hdr)

        for r in range(TABLE_ROW_COUNT - 1):
            item = QTableWidgetItem("")
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(r, COLUMN_NUMBER_ONE, item)

        item = QTableWidgetItem("Uпор, В")
        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        self.table.setItem(ROW_NUMBER_SIX, COLUMN_NUMBER_ONE, item)

        self.table_resistance = PasteTableWidget()
        self.table_resistance.setColumnCount(3)
        self.table_resistance.setHorizontalHeaderLabels(["Uзи, В", "Rом, Ω", "Rдин, Ω"])

        self.table_s = PasteTableWidget()
        self.table_s.setColumnCount(12)
        self.table_s.setHorizontalHeaderLabels(["9", "8", "7", "6", "5", "4", "3", "2", "1", "0.5", "0.2", "0.1"])

        delegate = NumberDelegate(self)
        self.table.setItemDelegate(delegate)
        self.table_s.setItemDelegate(delegate)
        self.table_resistance.setItemDelegate(delegate)

        self.current_row = 0
        self.current_col = 2

        self.btn_read = QPushButton("Снять значение")
        self.btn_read.clicked.connect(self.read_and_append)

        self.btn_plot_g = QPushButton("Стокозатворная характеристика")
        self.btn_plot_g.clicked.connect(self.plot_gate)

        self.btn_plot_out = QPushButton("Выходная характеристика")
        self.btn_plot_out.clicked.connect(self.plot_output)

        self.btn_calc_S = QPushButton("Расчет крутизны S")
        self.btn_calc_S.clicked.connect(self.on_calc_s)

        self.btn_calc_r = QPushButton("Расчет сопротивлений")
        self.btn_calc_r.clicked.connect(self.on_calc_resistance)

        self.button_formulas = QPushButton("Формулы")
        self.button_formulas.clicked.connect(self.show_formulas)

        self.btn_save_all = QPushButton("Сохранить всё в Excel")
        self.btn_save_all.clicked.connect(self.on_save_all)

        self.timer_label = QLabel("Время выполнения работы 00:00:00")

        self.btn_exit = QPushButton("Завершить работу")
        self.btn_exit.clicked.connect(self.close)

        vc = VoltageControl(on_submit=self.controller.set_voltage)

        left = QVBoxLayout()
        left.addWidget(QLabel("Стокозатворная и выходная характеристика полевого транзистора"))
        left.addWidget(self.table)
        left.addWidget(self.btn_read)

        left.addWidget(QLabel("Сопротивления"))
        left.addWidget(self.table_resistance)
        left.addWidget(QLabel("Крутизна S"))
        left.addWidget(self.table_s)

        right = QVBoxLayout()
        right.addWidget(self.btn_plot_g)
        right.addWidget(self.btn_plot_out)
        right.addWidget(self.btn_calc_r)
        right.addWidget(self.btn_calc_S)
        right.addWidget(self.button_formulas)
        right.addWidget(self.btn_save_all)
        right.addWidget(vc)
        right.addStretch()
        right.addWidget(self.timer_label)
        right.addWidget(self.btn_exit)

        main = QHBoxLayout(self)
        main.addLayout(left, 4)
        main.addLayout(right, 1)

        timer = QTimer(self)
        timer.timeout.connect(lambda: update_timer_label(self.start_time, self.timer_label))
        timer.start(1000)

    def read_and_append(self):
        try:
            m = self.controller.measure()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось снять данные: {e}")
            return

        col = self.current_col
        max_col = self.table.columnCount()

        hdr_item = self.table.horizontalHeaderItem(col)
        try:
            expected_u = float(hdr_item.text())
        except Exception:
            QMessageBox.warning(self, "Неправильный заголовок",
                                f"Невалидный header в колонке {col}")
            return

        if abs(expected_u - m.u_in) > THRESHOLD:
            QMessageBox.warning(
                self, "Несоответствие напряжения",
                f"Ожидалось Uси = {expected_u:.2f} В, а снято {m.u_in:.2f} В.\n"
                "Проверьте установку на стенде."
            )
            return

        if col < max_col:
            item = QTableWidgetItem(f"{m.i_out_mA:.3f}")
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(self.current_row, col, item)
        else:
            QMessageBox.warning(self, "Переполнение",
                                "Все колонки для Ic заполнены.")
            return

        self.current_col += 1
        if self.current_col >= max_col:
            self.current_col = 2
            self.current_row += 1
            if self.current_row >= self.table.rowCount():
                QMessageBox.information(self, "Готово", "Все строки заполнены.")
                self.btn_read.setEnabled(False)

    def plot_gate(self):

        Uzi = []
        for row in range(TABLE_ROW_COUNT - 1):
            it = self.table.item(row, COLUMN_NUMBER_ONE)
            try:
                Uzi.append(float(it.text()))
            except Exception:
                Uzi.append(None)

        wanted = {"0.1", "2", "5", "8"}

        for col in range(START_COLUMN, self.table.columnCount()):
            hdr = self.table.horizontalHeaderItem(col).text()
            if hdr not in wanted:
                continue
            Usi = float(hdr)

            Ic = []
            for row in range(TABLE_ROW_COUNT - 1):
                it = self.table.item(row, col)
                try:
                    Ic.append(float(it.text()))
                except Exception:
                    Ic.append(None)

            x = [u for u, i in zip(Uzi, Ic) if u is not None and i is not None]
            y = [i for u, i in zip(Uzi, Ic) if u is not None and i is not None]

            if len(x) == MIN_POINTS_TO_SHOW_PLOT:
                plt.plot(x, y, marker='o', linestyle='-', label=f"Uси={Usi:.1f} В")
            else:
                QMessageBox.information(
                    self, "Ошибка",
                    f"Недостаточно данных для построения графика (минимум {MIN_POINTS_TO_SHOW_PLOT} точек)"
                )
                return

        plt.xlabel("Uзи, В")
        plt.ylabel("Ic, мА")
        plt.title("Стокозатворная характеристика (выборочные Uси)")
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        plt.show()

    def plot_output(self):

        Usi = []
        for col in range(START_COLUMN, self.table.columnCount()):
            hdr = self.table.horizontalHeaderItem(col).text()
            try:
                Usi.append(float(hdr))
            except ValueError:
                Usi.append(None)

        for row in range(ROW_NUMBER_ONE, self.table.rowCount()):

            it_uzi = self.table.item(row, COLUMN_NUMBER_ONE)
            if not it_uzi or not it_uzi.text():
                continue
            try:
                Uzi = float(it_uzi.text())
            except ValueError:
                continue

            xs, ys = [], []
            for idx, col in enumerate(range(START_COLUMN, self.table.columnCount())):
                it_ic = self.table.item(row, col)
                if not it_ic or not it_ic.text():
                    continue
                try:
                    ic = float(it_ic.text())
                    usi = Usi[idx]
                except ValueError:
                    continue
                if usi is None:
                    continue
                xs.append(usi)
                ys.append(ic)

            if len(ys) >= MIN_POINTS_TO_SHOW_PLOT:
                plt.plot(xs, ys, marker='o', linestyle='-',
                         label=f"Uзи = {Uzi:.2f} В")
            else:
                QMessageBox.information(
                    self, "Ошибка",
                    f"Недостаточно данных для построения графика (минимум {MIN_POINTS_TO_SHOW_PLOT} точек)"
                )
                return

        plt.xlabel("Uси, В")
        plt.ylabel("Ic, мА")
        plt.title("Выходная характеристика полевого транзистора")
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        plt.show()

    def _extract_s_data(self) -> Dict[float, Tuple[List[float], List[float]]]:

        data = {}
        meas_rows = list(range(0, 5))
        for col in range(START_COLUMN, self.table.columnCount()):
            hdr_item = self.table.horizontalHeaderItem(col)
            if not hdr_item:
                continue
            try:
                Uce = float(hdr_item.text())
            except ValueError:
                continue

            Ube_vals, Ic_vals = [], []
            for row in meas_rows:
                item_u = self.table.item(row, COLUMN_NUMBER_ONE)
                item_ic = self.table.item(row, col)
                if not item_u or not item_ic:
                    continue
                try:
                    Ube_vals.append(float(item_u.text()))
                    Ic_vals.append(float(item_ic.text()))
                except ValueError:
                    continue

            data[Uce] = (Ube_vals, Ic_vals)
        return data

    def on_calc_s(self):
        data = self._extract_s_data()
        try:
            results = self.controller.compute_transconductance_s(data)
        except ValueError as e:
            QMessageBox.information(self, "Расчет S", str(e))
            return

        Uces = list(results.keys())
        s_lists = list(results.values())
        ube_vals = next(iter(data.values()))[0]

        self.table_s.setColumnCount(len(Uces))
        self.table_s.setRowCount(len(s_lists[0]))
        row_labels = [
            f"{ube_vals[i]:.2f}→{ube_vals[i + 1]:.2f}"
            for i in range(self.table_s.rowCount())
        ]
        self.table_s.setVerticalHeaderLabels(row_labels)
        for col, S_vals in enumerate(s_lists):
            for row, s in enumerate(S_vals):
                item = QTableWidgetItem(f"{s:.3f}")
                self.table_s.setItem(row, col, item)

    def _extract_resistance_data(self):
        hdr_to_col = {
            self.table.horizontalHeaderItem(c).text(): c
            for c in range(START_COLUMN, self.table.columnCount())
            if self.table.horizontalHeaderItem(c)
        }
        needed = ["0.1", "0.5", "6", "9"]
        missing = [h for h in needed if h not in hdr_to_col]
        if missing:
            raise ValueError(f"Не найдены столбцы: {', '.join(missing)}")

        data = []
        for row in range(ROW_NUMBER_ONE, ROW_NUMBER_SIX):
            item_u = self.table.item(row, COLUMN_NUMBER_ONE)
            if not item_u or not item_u.text():
                continue
            Uzi = float(item_u.text())

            I_lo = float(self.table.item(row, hdr_to_col["0.1"]).text() or 0)
            I_hi = float(self.table.item(row, hdr_to_col["0.5"]).text() or 0)
            I6 = float(self.table.item(row, hdr_to_col["6"]).text() or 0)
            I9 = float(self.table.item(row, hdr_to_col["9"]).text() or 0)

            data.append((Uzi, I_lo, I_hi, I6, I9))
        return data

    def on_calc_resistance(self):
        try:
            data = self._extract_resistance_data()
            results = self.controller.comp_resistances(data)
        except ValueError as e:
            QMessageBox.warning(self, "Расчет сопротивлений", str(e))
            return

        self.table_resistance.setRowCount(len(results))
        for r, (Uzi, R_ohm, R_dyn) in enumerate(results):
            self.table_resistance.setItem(r, 0, QTableWidgetItem(f"{Uzi:.2f}"))
            self.table_resistance.setItem(r, 1, QTableWidgetItem(
                f"{R_ohm:.2f}" if R_ohm is not None else "n/a"
            ))
            self.table_resistance.setItem(r, 2, QTableWidgetItem(
                f"{R_dyn:.2f}" if R_dyn is not None else "n/a"
            ))

    def show_formulas(self):
        self.formulas_window.show()

    def on_save_all(self):
        tables = {
            "Стокозатворная х-ка": self.table,
            "Крутизна S": self.table_s,
            "Сопротивления Rом и Rдин": self.table_resistance,
        }
        export_tables_to_excel(self, tables)
