from PyQt6.QtWidgets import (
    QWidget, QTableWidgetItem, QPushButton,
    QHBoxLayout, QVBoxLayout, QLabel, QMessageBox
)
from PyQt6.QtCore import Qt
from lab8.const_lab8 import *
from formulas.formulas_window import FormulasWindow
from lab8.controller_lab8 import Lab8Controller
from utils.excel_timer_helper import update_timer_label, export_tables_to_excel
from utils.paste_table_widget import PasteTableWidget
import matplotlib.pyplot as plt
from PyQt6.QtCore import QTimer
from datetime import datetime
from utils.table_validator import NumberDelegate


class Lab8Window(QWidget):
    def __init__(self):
        super().__init__()
        self.formulas_window = FormulasWindow(lab_number=8)
        self.controller = Lab8Controller()
        self.start_time = datetime.now()
        self.setWindowTitle("ЛР8: Статические ВАХ биполярного транзистора")

        self.table_input = PasteTableWidget(TABLE_INPUT_ROW_COUNT, TABLE_INPUT_COLUMN_COUNT)
        self.table_input.setHorizontalHeaderLabels([
            "Uкэ, В", "Iб, мкА", "0", "50", "100", "150", "200", "250"
        ])

        self.table_input.setSpan(0, 1, 4, 1)
        hdr = QTableWidgetItem("Uбэ, мВ")
        hdr.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        hdr.setFlags(hdr.flags() & ~Qt.ItemFlag.ItemIsEditable)
        self.table_input.setItem(0, 1, hdr)

        self.table_output = PasteTableWidget(TABLE_OUTPUT_ROW_COUNT, TABLE_OUTPUT_COLUMN_COUNT)
        self.table_output.setHorizontalHeaderLabels([
            "Uкэ, В", "Iб, мкА", "0", "50", "100", "150", "200", "250"
        ])
        self.table_output.setSpan(0, 1, 7, 1)
        hdr2 = QTableWidgetItem("Iк, мА")
        hdr2.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        hdr2.setFlags(hdr2.flags() & ~Qt.ItemFlag.ItemIsEditable)
        self.table_output.setItem(0, 1, hdr2)

        for u_val, row in INPUT_ROW_MAP.items():
            item = QTableWidgetItem(f"{u_val:.1f}")
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table_input.setItem(row, 0, item)

        for u_val, row in OUTPUT_ROW_MAP.items():
            item = QTableWidgetItem(f"{u_val:.1f}")
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table_output.setItem(row, 0, item)

        delegate = NumberDelegate(self)
        self.table_input.setItemDelegate(delegate)
        self.table_output.setItemDelegate(delegate)

        self.next_input_col = {r: 2 for r in INPUT_ROW_MAP.values()}
        self.next_output_col = {r: 2 for r in OUTPUT_ROW_MAP.values()}

        self.btn_read = QPushButton("Снять значение")
        self.btn_read.clicked.connect(self.read_both)

        self.btn_plot_in = QPushButton("Входная характеристика")
        self.btn_plot_in.clicked.connect(self.show_plot_in)

        self.btn_plot_out = QPushButton("Выходная характеристика")
        self.btn_plot_out.clicked.connect(self.show_plot_out)

        self.btn_avg_beta = QPushButton("Средний β базы")
        self.btn_avg_beta.clicked.connect(self.on_avg_beta)

        self.button_formulas = QPushButton("Формулы")
        self.button_formulas.clicked.connect(self.show_formulas)

        self.btn_save_all = QPushButton("Сохранить всё в Excel")
        self.btn_save_all.clicked.connect(self.on_save_all)

        self.timer_label = QLabel("Время выполнения работы 0:00:00")

        self.btn_exit = QPushButton("Завершить работу")
        self.btn_exit.clicked.connect(self.close)

        left = QVBoxLayout()
        left.addWidget(QLabel("Входная характеристика"))
        left.addWidget(self.table_input)
        left.addSpacing(10)
        left.addWidget(QLabel("Выходная характеристика"))
        left.addWidget(self.table_output)
        left.addWidget(self.btn_read)

        right = QVBoxLayout()
        right.addWidget(self.btn_plot_in)
        right.addWidget(self.btn_plot_out)
        right.addWidget(self.btn_avg_beta)
        right.addWidget(self.button_formulas)
        right.addWidget(self.btn_save_all)
        right.addStretch()
        right.addWidget(self.timer_label)
        right.addWidget(self.btn_exit)

        main = QHBoxLayout(self)
        main.addLayout(left, 3)
        main.addLayout(right, 1)

        timer = QTimer(self)
        timer.timeout.connect(lambda: update_timer_label(self.start_time, self.timer_label))
        timer.start(1000)

    def read_both(self):
        try:
            m = self.controller.measure()

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось снять данные: {e}")
            return

        in_row = INPUT_ROW_MAP.get(float(m.u_in).__round__(1))
        out_row = OUTPUT_ROW_MAP.get(float(m.u_in).__round__(1))
        if in_row is None and out_row is None:
            QMessageBox.warning(
                self, "Неверное Uкэ",
                f"Uкэ={m.u_in:.3f} В отсутствует в конфигурации таблиц."
            )
            return

        if in_row is not None:
            col = self.next_input_col[in_row]
            if col < self.table_input.columnCount():
                self.table_input.setItem(
                    in_row, col,
                    QTableWidgetItem(f"{m.u_out:.3f}")
                )
                self.next_input_col[in_row] += 1
            else:
                QMessageBox.warning(
                    self, "Переполнение",
                    f"Входная: строка Uкэ={m.u_in} заполнена."
                )

        if out_row is not None:
            col = self.next_output_col[out_row]
            if col < self.table_output.columnCount():
                self.table_output.setItem(
                    out_row, col,
                    QTableWidgetItem(f"{m.i_out_mA:.3f}")
                )
                self.next_output_col[out_row] += 1
            else:
                QMessageBox.warning(
                    self, "Переполнение",
                    f"Выходная: строка Uкэ={m.u_in} заполнена."
                )

    def show_plot_in(self):

        ib_vals = []
        for col in range(START_COLUMN, self.table_input.columnCount()):
            hdr = self.table_input.horizontalHeaderItem(col).text()
            try:
                ib_vals.append(float(hdr))
            except ValueError:
                pass

        for u_ce, row in INPUT_ROW_MAP.items():
            x_u_be = []
            y_i_b = []
            for idx, col in enumerate(range(START_COLUMN, self.table_input.columnCount())):
                item = self.table_input.item(row, col)
                if item and item.text():
                    try:
                        u_be = float(item.text())
                        i_b = ib_vals[idx]
                    except ValueError:
                        continue
                    x_u_be.append(u_be)
                    y_i_b.append(i_b)

            if len(x_u_be) < MIN_POINTS_TO_SHOW_PLOT or len(y_i_b) < MIN_POINTS_TO_SHOW_PLOT:
                QMessageBox.information(
                    self, "Ошибка",
                    f"Недостаточно данных для построения графика (минимум {MIN_POINTS_TO_SHOW_PLOT} точек)"
                )
                return

            if x_u_be and y_i_b:
                plt.plot(
                    x_u_be, y_i_b,
                    marker='o', linestyle='-',
                    label=f"Uкэ = {u_ce} В"
                )

        plt.xlabel("Uбэ, В")
        plt.ylabel("Iб, мкА")
        plt.title("Входная характеристика биполярного транзистора")
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        plt.show()

    def show_plot_out(self):

        for col in range(START_COLUMN, self.table_output.columnCount()):
            try:
                ib_header = float(self.table_output.horizontalHeaderItem(col).text())
            except:
                continue

            x_Uce = []
            y_Ic = []
            for row in OUTPUT_ROW_MAP.values():
                item_u = self.table_output.item(row, 0)
                item_ic = self.table_output.item(row, col)
                if not item_u or not item_ic:
                    continue
                try:
                    u_ce = float(item_u.text())
                    ic = float(item_ic.text())
                except ValueError:
                    continue
                x_Uce.append(u_ce)
                y_Ic.append(ic)

            if len(x_Uce) < MIN_POINTS_TO_SHOW_PLOT or len(y_Ic) < MIN_POINTS_TO_SHOW_PLOT:
                QMessageBox.information(
                    self, "Ошибка",
                    f"Недостаточно данных для построения графика (минимум {MIN_POINTS_TO_SHOW_PLOT} точек)"
                )
                return

            if x_Uce and y_Ic:
                plt.plot(
                    x_Uce, y_Ic,
                    marker='o', linestyle='-',
                    label=f"Iб={ib_header:.0f} µA"
                )

        plt.xlabel("Uкэ, В")
        plt.ylabel("Iк, мА")
        plt.title("Выходная характеристика биполярного транзистора")
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        plt.show()

    def _extract_beta_data(self):
        data = []
        for u_ce, row in OUTPUT_ROW_MAP.items():
            ic_vals, ib_vals = [], []
            for col in range(START_COLUMN, self.table_output.columnCount()):
                item_ic = self.table_output.item(row, col)
                hdr = self.table_output.horizontalHeaderItem(col)
                if not item_ic or not item_ic.text() or not hdr:
                    continue
                try:
                    ic = float(item_ic.text())
                    ib_uA = float(hdr.text())
                except ValueError:
                    continue
                ib = ib_uA * 1e-3  # мА
                ic_vals.append(ic)
                ib_vals.append(ib)
            data.append((u_ce, ic_vals, ib_vals))
        return data

    def on_avg_beta(self):
        data = self._extract_beta_data()
        try:
            results = self.controller.avg_beta(data)
        except ValueError as e:
            QMessageBox.information(self, "Средние β", str(e))
            return

        text = "\n".join(f"Uкэ={u_ce:.1f} В → β≈{beta:.1f}" for u_ce, beta in results)
        QMessageBox.information(self, "Средние β по строкам", text)

    def show_formulas(self):
        self.formulas_window.show()

    def on_save_all(self):
        tables = {
            "Входная х-ка]": self.table_input,
            "Выходная х-ка": self.table_output,
        }
        export_tables_to_excel(self, tables)
