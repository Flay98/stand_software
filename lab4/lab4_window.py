import numpy as np
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, \
    QMessageBox
from matplotlib import pyplot as plt

from utils.paste_table_widget import PasteTableWidget
from formulas.formulas_window import FormulasWindow
from utils.stand_controller import StandController


class Lab4Window(QWidget):
    def __init__(self):
        super().__init__()
        self.controller = StandController()
        self.setWindowTitle("Лабораторная работа №4. Исследование ВАХ стабилизатора")
        self.resize(1200, 700)
        self.row = 0
        self.current_output_col = 0

        # ----------- Таблица 1: Амплитудная характеристика ----------
        self.table_amplitude = PasteTableWidget(48, 3)
        self.table_amplitude.setHorizontalHeaderLabels(["Uпит, В", "Uнагр, В", "Iнагр, мА"])
        self.button_read_amplitude = QPushButton("Снять значение (амплитудная)")
        self.button_read_amplitude.clicked.connect(self.read_from_stand_table_amplitude)

        # ----------- Таблица 2: Выходная характеристика ----------
        self.table_output = PasteTableWidget(9, 8)
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
            self.table_output.setItem(0, col, item)

        # ----------- Кнопки справа ----------
        self.button_plot_vh = QPushButton("Зависимость напряжения на нагрузке от напряжения питания")
        self.button_plot_vh.clicked.connect(self.show_plot_vh)
        self.button_k_st = QPushButton("Найти коэффициент стабилизации на участке стабилизации")
        self.button_k_st.clicked.connect(self.calculate_stabilization_coefficient)
        self.button_p_vh = QPushButton("Посчитать входную мощность")
        self.button_p_vh.clicked.connect(self.calculate_input_power)
        self.button_p_vyh = QPushButton("Посчитать выходную мощность")
        self.button_p_vyh.clicked.connect(self.calculate_output_power)
        self.button_calc_efficiency = QPushButton("Посчитать КПД")
        self.button_calc_efficiency.clicked.connect(self.calculate_efficiency)
        self.button_i_st = QPushButton("Посчитать ток стабилизатора")
        self.button_i_st.clicked.connect(self.calculate_stabilization_current)
        self.button_plot = QPushButton("Построить график выходной характеристики")
        self.button_plot.clicked.connect(self.show_plot_vyh)
        self.button_formulas = QPushButton("Формулы")
        self.button_formulas.clicked.connect(self.show_formulas)
        self.button_exit = QPushButton("Завершить работу")
        self.button_exit.clicked.connect(self.close)

        # ----------- Размещение ----------
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
        layout_side.addStretch()
        layout_side.addWidget(self.button_exit)

        layout_main.addLayout(layout_tables, 3)
        layout_main.addLayout(layout_side, 1)
        self.setLayout(layout_main)

    def show_plot_vh(self):
        u_pit_vals = []
        u_load_vals = []

        for row in range(self.table_amplitude.rowCount()):
            item_u_pit = self.table_amplitude.item(row, 0)
            item_u_load = self.table_amplitude.item(row, 1)
            if item_u_pit and item_u_load:
                try:
                    u_pit = float(item_u_pit.text())
                    u_load = float(item_u_load.text())
                    u_pit_vals.append(u_pit)
                    u_load_vals.append(u_load)
                except ValueError:
                    continue

        if len(u_pit_vals) < 2:
            print("Недостаточно данных для построения графика")
            return

        plt.figure(figsize=(8, 6))
        plt.plot(u_pit_vals, u_load_vals, marker='o', linestyle='-')
        plt.xlabel("Uпит, В")
        plt.ylabel("Uнагр, В")
        plt.title("Зависимость напряжения на нагрузке от напряжения питания")
        plt.grid(True)
        plt.tight_layout()
        plt.show()

    def calculate_stabilization_coefficient(self):

        u_pit = []
        u_load = []

        for row in range(self.table_amplitude.rowCount()):
            it_p = self.table_amplitude.item(row, 0)
            it_l = self.table_amplitude.item(row, 1)
            if it_p and it_l:
                try:
                    u_pit.append(float(it_p.text()))
                    u_load.append(float(it_l.text()))
                except ValueError:
                    continue

        n = len(u_load)
        if n < 2:
            print("Недостаточно данных")
            return

        threshold = 0.01
        start = None
        for i in range(n - 1):
            if abs(u_load[i+1] - u_load[i]) < threshold:
                start = i
                break
        if start is None:
            print("Участок стабилизации не найден")
            return

        k_values = []
        for i in range(start-1, n - 1):
            delta_p = u_pit[i+1] - u_pit[i]
            avg_p = (u_pit[i+1] + u_pit[i]) / 2
            delta_l = u_load[i+1] - u_load[i]
            avg_l = (u_load[i+1] + u_load[i]) / 2

            if delta_l == 0 or avg_p == 0 or avg_l == 0:
                continue

            rel_p = delta_p / avg_p
            rel_l = delta_l / avg_l
            k_rel = rel_p / rel_l
            k_values.append(k_rel)

        if not k_values:
            print("Не удалось вычислить ни одного относительного Kст")
            return

        k_avg = sum(k_values) / len(k_values)

        msg = (
            f"Начало стабилизации: строка {start}\n"
            f"Посчитано {len(k_values)} относительных коэффициентов стабилизации\n"
            f"Среднее Kст = {k_avg:.2f}"
        )
        print(msg)
        QMessageBox.information(self, "Относительный коэффициент стабилизации", msg)

    def show_formulas(self):
        self.formulas_window = FormulasWindow(lab_number=4)
        self.formulas_window.show()

    def read_and_append_row(self, table, row_index):
        try:
            u_in, u_out, i_out = self.controller.get_voltage_current()
            print(f"Uвх = {u_in:.3f} В, Uвых = {u_out:.3f} В, Iвых = {i_out:.3f} мА")

            if row_index < table.rowCount():
                table.setItem(row_index, 0, QTableWidgetItem(f"{u_in:.3f}"))
                table.setItem(row_index, 1, QTableWidgetItem(f"{u_out:.3f}"))
                table.setItem(row_index, 2, QTableWidgetItem(f"{i_out:.3f}"))
                row_index += 1

        except RuntimeError as e:
            print(str(e))

        return row_index

    def read_and_append_column(self, table: QTableWidget, col_index: int):
        try:
            u_pit, u_nagr, i_nagr = self.controller.get_voltage_current()
            print(f"Uпит = {u_pit:.3f} В, Uнагр = {u_nagr:.3f} В, Iнагр = {i_nagr:.3f} мА")

            if col_index < table.columnCount():
                table.setItem(1, col_index, QTableWidgetItem(f"{u_pit:.3f}"))
                table.setItem(3, col_index, QTableWidgetItem(f"{u_nagr:.3f}"))
                table.setItem(4, col_index, QTableWidgetItem(f"{i_nagr:.3f}"))
                col_index += 1

        except RuntimeError as e:
            print(f"Ошибка при чтении со стенда: {e}")

        return col_index

    def read_from_stand_table_output(self):
        self.current_output_col = self.read_and_append_column(self.table_output, self.current_output_col)

    def read_from_stand_table_amplitude(self):
        self.row = self.read_and_append_row(self.table_amplitude, self.row)

    def _read_output_table(self):
        data = []
        for col in range(self.table_output.columnCount()):
            try:
                u_pit = float(self.table_output.item(1, col).text())
                i_pit = float(self.table_output.item(2, col).text()) / 1000  # мА→А
                u_nagr = float(self.table_output.item(3, col).text())
                i_nagr = float(self.table_output.item(4, col).text()) / 1000  # мА→А
            except Exception:
                continue
            data.append((col, u_pit, i_pit, u_nagr, i_nagr))
        return data

    def calculate_input_power(self):
        for col, u_pit, i_pit, *_ in self._read_output_table():
            p_in = u_pit * i_pit
            self.table_output.setItem(5, col, QTableWidgetItem(f"{p_in:.3f}"))

    def calculate_output_power(self):
        for col, *_, u_nagr, i_nagr in self._read_output_table():
            p_out = u_nagr * i_nagr
            self.table_output.setItem(6, col, QTableWidgetItem(f"{p_out:.3f}"))

    def calculate_efficiency(self):
        for col, u_pit, i_pit, u_nagr, i_nagr in self._read_output_table():
            p_in = u_pit * i_pit
            p_out = u_nagr * i_nagr
            eta = (p_out / p_in) if p_in != 0 else 0
            self.table_output.setItem(7, col, QTableWidgetItem(f"{eta:.3f}"))

    def calculate_stabilization_current(self):
        for col, u_pit, i_pit, u_nagr, i_nagr in self._read_output_table():
            i_st = (i_pit - i_nagr) * 1000
            self.table_output.setItem(8, col, QTableWidgetItem(f"{i_st:.3f}"))

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

            item_u = self.table_output.item(3, col)
            U_nagr.append(float(item_u.text()) if item_u else np.nan)

            item_i = self.table_output.item(4, col)
            I_nagr.append(float(item_i.text()) if item_i else np.nan)

        Rn = np.array(Rn)
        U_nagr = np.array(U_nagr)
        I_nagr = np.array(I_nagr)

        mask1 = (~np.isnan(U_nagr)) & (~np.isnan(Rn)) & (Rn != np.inf)
        mask2 = (~np.isnan(U_nagr)) & (~np.isnan(I_nagr))

        # --- График 1: Uнагр = f(Rн) ---
        if mask1.sum() >= 2:
            plt.figure(figsize=(8, 5))
            plt.plot(Rn[mask1], U_nagr[mask1], 'o-', label="Uнаг \u2192 Rн")
            plt.xlabel("Rн, Ом")
            plt.ylabel("Uнагр, В")
            plt.title("Зависимость напряжения нагрузки от сопротивления")
            plt.grid(True)
            plt.tight_layout()
            plt.show()
        else:
            print("Недостаточно данных для графика Uнагр = f(Rн)")

        # --- График 2: Uнагр = f(Iнагр) ---
        if mask2.sum() >= 2:
            plt.figure(figsize=(8, 5))
            plt.plot(I_nagr[mask2], U_nagr[mask2], 's-', label="Uнаг \u2192 Iнаг")
            plt.xlabel("Iнагр, мА")
            plt.ylabel("Uнагр, В")
            plt.title("Зависимость напряжения нагрузки от тока нагрузки")
            plt.grid(True)
            plt.tight_layout()
            plt.show()
        else:
            print("Недостаточно данных для графика Uнагр = f(Iнагр)")

