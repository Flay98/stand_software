from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidgetItem
)
from paste_table_widget import PasteTableWidget
from formulas_window import FormulasWindow
from stand_controller import StandController


class Lab2Window(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Лабораторная работа №2. Исследование стабилитрона")
        self.resize(1000, 600)
        self.controller = StandController()
        self.row = 0

        self.table_vah = PasteTableWidget(46, 3)
        self.table_vah.setHorizontalHeaderLabels(["Uвх, В", "Uвых, В", "Iвых, мА"])
        self.table_vah.setMaximumWidth(350)

        self.table_rd = PasteTableWidget(46, 4)
        self.table_rd.setHorizontalHeaderLabels(["Uвых, В", "Iвых, мА", "rd (ΔU/ΔI), Ом", "rd (nUt/Id), Ом"])
        self.table_rd.setMaximumWidth(500)

        self.button_measure = QPushButton("Снять значение")
        self.button_measure.clicked.connect(self.read_from_stand)  # пока пустой

        self.button_plot = QPushButton("Построить ВАХ стабилитрона")
        self.button_plot.clicked.connect(self.plot_vah)  # пока пустой

        self.button_calc_rd = QPushButton("Рассчитать динамическое сопротивление")
        self.button_calc_rd.clicked.connect(self.calculate_rd)  # пока пустой

        self.button_formulas = QPushButton("Формулы")
        self.button_formulas.clicked.connect(self.show_formulas_window)

        self.button_find_stabilization = QPushButton("Найти начало стабилизации")
        self.button_find_stabilization.clicked.connect(self.find_stabilization_start)

        self.button_exit = QPushButton("Завершить выполнение работы")
        self.button_exit.clicked.connect(self.close)

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
        side_layout.addStretch()
        side_layout.addWidget(self.button_exit)

        main_layout.addLayout(table_layout, 3)
        main_layout.addLayout(side_layout, 1)
        self.setLayout(main_layout)

    def read_from_stand(self):
        try:
            u_in, u_out, i_out = self.controller.get_voltage_current()
            print(f"Uвх = {u_in:.3f} В, Uвых = {u_out:.3f} В, Iвых = {i_out:.3f} мА")

            if self.row < self.table_vah.rowCount():
                self.table_vah.setItem(self.row, 0, QTableWidgetItem(f"{u_in:.3f}"))
                self.table_vah.setItem(self.row, 1, QTableWidgetItem(f"{u_out:.3f}"))
                self.table_vah.setItem(self.row, 2, QTableWidgetItem(f"{i_out:.3f}"))
                self.row += 1

        except RuntimeError as e:
            print(f"Ошибка при считывании данных со стенда: {e}")

    def plot_vah(self):
        u_vals = []
        i_vals = []

        for row in range(self.table_vah.rowCount()):
            try:
                u_item = self.table_vah.item(row, 1)
                i_item = self.table_vah.item(row, 2)
                if u_item and i_item:
                    u = float(u_item.text())
                    i = float(i_item.text())
                    u_vals.append(u)
                    i_vals.append(i)
            except ValueError:
                continue

        if len(u_vals) < 2:
            print("Недостаточно данных для построения графика")
            return

        import matplotlib.pyplot as plt
        plt.figure(figsize=(8, 6))
        plt.plot(u_vals, i_vals, marker='o', linestyle='-', label='ВАХ стабилитрона')
        plt.xlabel("Uвых, В")
        plt.ylabel("Iвых, мА")
        plt.title("ВАХ стабилитрона")
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        plt.show()

    def calculate_rd(self):
        U = []
        I_mA = []

        for row in range(self.table_vah.rowCount()):
            try:
                u_item = self.table_vah.item(row, 1)
                i_item = self.table_vah.item(row, 2)
                if u_item and i_item:
                    u = float(u_item.text())
                    i = float(i_item.text())
                    U.append(u)
                    I_mA.append(i)
            except ValueError:
                continue

        if len(U) < 2:
            print("Недостаточно данных для расчёта rd")
            return

        # Очистка таблицы
        self.table_rd.clearContents()
        self.table_rd.setRowCount(len(U) - 1)

        Ut = 0.0253
        n = 1.0

        for i in range(len(U) - 1):
            try:
                delta_U = U[i + 1] - U[i]
                delta_I = (I_mA[i + 1] - I_mA[i]) * 0.001
                rd_delta = delta_U / delta_I if delta_I != 0 else float('inf')

                I_A = I_mA[i] * 0.001
                rd_theor = (n * Ut) / I_A if I_A > 0 else float('inf')

                self.table_rd.setItem(i, 0, QTableWidgetItem(f"{U[i]:.3f}"))
                self.table_rd.setItem(i, 1, QTableWidgetItem(f"{I_mA[i]:.3f}"))
                self.table_rd.setItem(i, 2, QTableWidgetItem(f"{rd_delta:.3f}"))
                self.table_rd.setItem(i, 3, QTableWidgetItem(f"{rd_theor:.3f}"))

            except Exception as e:
                print(f"Ошибка на строке {i}: {e}")

    def show_formulas_window(self):
        self.formulas_window = FormulasWindow(lab_number=2)
        self.formulas_window.show()

    def find_stabilization_start(self):
        u_vals = []
        i_vals = []

        for row in range(self.table_vah.rowCount()):
            try:
                u = float(self.table_vah.item(row, 1).text())
                i = float(self.table_vah.item(row, 2).text())
                u_vals.append(u)
                i_vals.append(i)
            except:
                continue

        if len(u_vals) < 2:
            print("Недостаточно данных для анализа стабилизации")
            return

        stab_start_index = None
        for i in range(len(u_vals) - 1):
            delta_u = u_vals[i + 1] - u_vals[i]
            delta_i = (i_vals[i + 1] - i_vals[i]) * 0.001  # мА → А
            if delta_i == 0:
                continue
            rd = delta_u / delta_i
            if rd < 5:
                stab_start_index = i
                break

        if stab_start_index is None:
            print("Участок стабилизации не найден")
            return

        self.plot_stabilization_region(u_vals, i_vals, stab_start_index)
        self.recalculate_rd_for_stabilization(u_vals, i_vals, stab_start_index)

    def plot_stabilization_region(self, u_vals, i_vals, stab_start_index):
        import matplotlib.pyplot as plt

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

    def recalculate_rd_for_stabilization(self, u_vals, i_vals, start_index):
        Ut = 0.0253
        n = 1.0

        u_slice = u_vals[start_index:]
        i_slice = i_vals[start_index:]

        self.table_rd.clearContents()
        self.table_rd.setRowCount(len(u_slice) - 1)

        rd_list = []

        for i in range(len(u_slice) - 1):
            try:
                delta_U = u_slice[i + 1] - u_slice[i]
                delta_I = (i_slice[i + 1] - i_slice[i]) * 0.001
                rd_delta = delta_U / delta_I if delta_I != 0 else float('inf')
                rd_list.append(rd_delta)

                I_A = i_slice[i] * 0.001
                rd_theor = (n * Ut) / I_A if I_A > 0 else float('inf')

                self.table_rd.setItem(i, 0, QTableWidgetItem(f"{u_slice[i]:.3f}"))
                self.table_rd.setItem(i, 1, QTableWidgetItem(f"{i_slice[i]:.3f}"))
                self.table_rd.setItem(i, 2, QTableWidgetItem(f"{rd_delta:.3f}"))
                self.table_rd.setItem(i, 3, QTableWidgetItem(f"{rd_theor:.3f}"))

            except Exception as e:
                print(f"Ошибка при расчёте rd: {e}")

        if rd_list:
            rd_avg = sum(rd_list) / len(rd_list)
            print(f"Среднее rd по участку стабилизации (ΔU/ΔI): {rd_avg:.3f} Ом")
        else:
            print("Не удалось вычислить среднее rd: нет данных.")
