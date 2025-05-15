from PyQt6.QtWidgets import (
    QWidget, QTableWidgetItem, QPushButton,
    QHBoxLayout, QVBoxLayout, QLabel, QMessageBox
)
from PyQt6.QtCore import Qt

from formulas.formulas_window import FormulasWindow
from utils.paste_table_widget import PasteTableWidget
from utils.stand_controller import StandController
import matplotlib.pyplot as plt


class Lab8Window(QWidget):
    def __init__(self):
        super().__init__()
        self.formulas_window = FormulasWindow(lab_number=8)
        self.controller = StandController()
        self.setWindowTitle("ЛР8: Статические ВАХ биполярного транзистора")
        self.resize(1000, 500)

        # 1) Таблица входной характеристики (4 строки, 8 столбцов)
        self.table_input = PasteTableWidget(4, 8)
        self.table_input.setHorizontalHeaderLabels([
            "Uкэ, В", "Iб, мкА", "0", "50", "100", "150", "200", "250"
        ])
        # объединяем весь столбец Iб
        self.table_input.setSpan(0, 1, 4, 1)
        hdr = QTableWidgetItem("Uбэ, мВ")
        hdr.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        hdr.setFlags(hdr.flags() & ~Qt.ItemFlag.ItemIsEditable)
        self.table_input.setItem(0, 1, hdr)

        # 2) Таблица выходной характеристики (7 строк, 8 столбцов)
        self.table_output = PasteTableWidget(7, 8)
        self.table_output.setHorizontalHeaderLabels([
            "Uкэ, В", "Iб, мкА", "0", "50", "100", "150", "200", "250"
        ])
        self.table_output.setSpan(0, 1, 7, 1)
        hdr2 = QTableWidgetItem("Iк, мА")
        hdr2.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        hdr2.setFlags(hdr2.flags() & ~Qt.ItemFlag.ItemIsEditable)
        self.table_output.setItem(0, 1, hdr2)

        # 3) Маппинг Uкэ→строка
        self.input_row_map = {0.0: 0, 1.0: 1, 6.0: 2, 12.0: 3}
        self.output_row_map = {
            0.1: 0, 0.2: 1, 0.3: 2, 0.5: 3, 1.0: 4, 6.0: 5, 12.0: 6
        }

        # 4) Предзаполняем столбец 0 (U_in) и делаем его readonly
        for u_val, row in self.input_row_map.items():
            item = QTableWidgetItem(f"{u_val:.1f}")
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table_input.setItem(row, 0, item)

        for u_val, row in self.output_row_map.items():
            item = QTableWidgetItem(f"{u_val:.1f}")
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table_output.setItem(row, 0, item)

        # 5) Для каждой строки храним указатель на следующий свободный столбец
        self.next_input_col = {r: 2 for r in self.input_row_map.values()}
        self.next_output_col = {r: 2 for r in self.output_row_map.values()}

        # 6) Кнопка съёма
        self.btn_read = QPushButton("Снять значение")
        self.btn_read.clicked.connect(self.read_both)

        # 7) Кнопки справа
        self.btn_plot_in = QPushButton("Входная характеристика")
        self.btn_plot_in.clicked.connect(self.show_plot_in)

        self.btn_plot_out = QPushButton("Выходная характеристика")
        self.btn_plot_out.clicked.connect(self.show_plot_out)
        self.btn_avg_beta = QPushButton("Средний β базы")
        self.btn_avg_beta.clicked.connect(self.avg_beta)
        self.button_formulas = QPushButton("Формулы")
        self.button_formulas.clicked.connect(self.show_formulas)
        self.btn_exit = QPushButton("Завершить работу")
        self.btn_exit.clicked.connect(self.close)

        # 8) Layout
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
        right.addStretch()
        right.addWidget(self.btn_exit)

        main = QHBoxLayout(self)
        main.addLayout(left, 3)
        main.addLayout(right, 1)

    def read_both(self):
        """Снятие (u_in,u_out,i_out) и запись в нужные таблицы."""
        try:
            u_in, u_out, i_out = self.controller.get_voltage_current()

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось снять данные: {e}")
            return

        # Проверка валидности u_in
        in_row = self.input_row_map.get(float(u_in).__round__(1))
        out_row = self.output_row_map.get(float(u_in).__round__(1))
        if in_row is None and out_row is None:
            QMessageBox.warning(
                self, "Неверное Uкэ",
                f"Uкэ={u_in:.3f} В отсутствует в конфигурации таблиц."
            )
            return

        # Запись в входную
        if in_row is not None:
            col = self.next_input_col[in_row]
            if col < self.table_input.columnCount():
                self.table_input.setItem(
                    in_row, col,
                    QTableWidgetItem(f"{u_out:.3f}")
                )
                self.next_input_col[in_row] += 1
            else:
                QMessageBox.warning(
                    self, "Переполнение",
                    f"Входная: строка Uкэ={u_in} заполнена."
                )

        # Запись в выходную
        if out_row is not None:
            col = self.next_output_col[out_row]
            if col < self.table_output.columnCount():
                self.table_output.setItem(
                    out_row, col,
                    QTableWidgetItem(f"{i_out:.3f}")
                )
                self.next_output_col[out_row] += 1
            else:
                QMessageBox.warning(
                    self, "Переполнение",
                    f"Выходная: строка Uкэ={u_in} заполнена."
                )

    def show_plot_in(self):

        # 1) Считываем шкалу Iб из заголовков столбцов 2…N
        ib_vals = []
        for col in range(2, self.table_input.columnCount()):
            hdr = self.table_input.horizontalHeaderItem(col).text()
            try:
                ib_vals.append(float(hdr))
            except ValueError:
                pass  # на случай пустых или некорректных заголовков

        # 2) Для каждой строки Uкэ строим свою ветку Iб = f(Uбэ)
        for u_ce, row in self.input_row_map.items():
            x_u_be = []
            y_i_b = []
            for idx, col in enumerate(range(2, self.table_input.columnCount())):
                item = self.table_input.item(row, col)
                if item and item.text():
                    try:
                        u_be = float(item.text())
                        i_b = ib_vals[idx]
                    except ValueError:
                        continue
                    x_u_be.append(u_be)
                    y_i_b.append(i_b)

            if x_u_be and y_i_b:
                plt.plot(
                    x_u_be, y_i_b,
                    marker='o', linestyle='-',
                    label=f"Uкэ = {u_ce} В"
                )

        # 3) Оформление графика
        plt.xlabel("Uбэ, В")
        plt.ylabel("Iб, мкА")
        plt.title("Входная характеристика биполярного транзистора")
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        plt.show()

    def show_plot_out(self):
        import matplotlib.pyplot as plt

        # Для каждой колонки Iб (начиная с 2) строим ветку Ic = f(Uce)
        for col in range(2, self.table_output.columnCount()):
            # получаем Iб из заголовка (µA → mA)
            try:
                ib_header = float(self.table_output.horizontalHeaderItem(col).text())
            except:
                continue
            ib_mA = ib_header * 1e-3  # µA → mA

            x_Uce = []
            y_Ic = []
            # пробегаем по всем строкам, где есть Uce
            for row in self.output_row_map.values():
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

    def avg_beta(self):
        """
        Для каждого Uкэ (каждой строки таблицы_output) считает β = Ic / Ib
        по всем ненулевым столбцам в этой строке и выводит среднее.
        """
        from PyQt6.QtWidgets import QMessageBox

        results = []
        for u_ce, row in self.output_row_map.items():
            betas = []
            # проходим по всем столбцам данных (2…N)
            for col in range(2, self.table_output.columnCount()):
                # ток коллектора
                item_ic = self.table_output.item(row, col)
                if not item_ic or not item_ic.text():
                    continue
                try:
                    ic_mA = float(item_ic.text())  # уже в мА
                except ValueError:
                    continue

                # ток базы из заголовка колонки (µA → мА)
                hdr = self.table_output.horizontalHeaderItem(col).text()
                try:
                    ib_uA = float(hdr)
                except ValueError:
                    continue
                ib_mA = ib_uA * 1e-3
                if ib_mA <= 0:
                    continue

                betas.append(ic_mA / ib_mA)

            if betas:
                avg_b = sum(betas) / len(betas)
                results.append((u_ce, avg_b))

        if not results:
            QMessageBox.information(self, "Средние β", "Нет достаточных данных для расчёта β.")
            return

        # форматируем вывод: строка Uкэ и средний β
        text = "\n".join(f"Uкэ={u_ce:.1f} В → β≈{beta:.1f}" for u_ce, beta in results)
        QMessageBox.information(self, "Средние β по строкам", text)

    def show_formulas(self):
        self.formulas_window.show()