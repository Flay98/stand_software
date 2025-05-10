from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidgetItem, QMessageBox
)
from PyQt6.QtCore import Qt
from matplotlib import pyplot as plt

from formulas_window import FormulasWindow
from paste_table_widget import PasteTableWidget  # ваша реализация PasteTableWidget
from stand_controller import StandController        # ваш контроллер для стенда


class Lab9Window(QWidget):
    def __init__(self):
        super().__init__()
        self.formulas_window = FormulasWindow(lab_number=9)
        self.controller = StandController()
        self.setWindowTitle("Исследование статических вольтамперных характеристик полевого транзистора")
        self.resize(1200, 400)

        headers = ["Uзи, В", "Uси, В"] + ["9", "8", "7", "6", "5", "4", "3", "2", "1", "0.5", "0.2", "0.1"]
        self.table = PasteTableWidget(6, len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setSpan(0, 1, 5, 1)
        hdr = QTableWidgetItem("Ic, мA")
        hdr.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        hdr.setFlags(hdr.flags() & ~Qt.ItemFlag.ItemIsEditable)
        self.table.setItem(0, 1, hdr)

        # строковые метки (Uзи вручную)
        # оставляем их пустыми — студенты заполнят вручную
        for r in range(5):
            item = QTableWidgetItem("")
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(r, 0, item)
        # последняя строка — Uпор, В, тоже вручную или можно по коду
        item = QTableWidgetItem("Uпор, В")
        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        self.table.setItem(5, 0, item)

        self.current_row = 0  # начинаем со второй строки
        self.current_col = 2  # после Uзи и Uси

        # Снять значение
        self.btn_read = QPushButton("Снять значение")
        self.btn_read.clicked.connect(self.read_and_append)

        # Новые кнопки справа
        self.btn_plot_g = QPushButton("Стокозатворная характеристика")
        self.btn_plot_g.clicked.connect(self.plot_gate)
        self.btn_plot_out = QPushButton("Выходная характеристика")
        self.btn_plot_out.clicked.connect(self.plot_output)
        self.btn_calc_S = QPushButton("Расчет крутизны S")
        self.btn_calc_S.clicked.connect(self.calc_S)
        self.btn_calc_r = QPushButton("Расчет сопротивлений")
        self.btn_calc_r.clicked.connect(self.calc_resistance)
        self.button_formulas = QPushButton("Формулы")
        self.button_formulas.clicked.connect(self.show_formulas)
        self.btn_exit = QPushButton("Завершить работу")
        self.btn_exit.clicked.connect(self.close)

        # Layout
        left = QVBoxLayout()
        left.addWidget(QLabel("Стокозатворная и выходная характеристика полевого транзистора"))
        left.addWidget(self.table)
        left.addWidget(self.btn_read)

        right = QVBoxLayout()
        right.addWidget(self.btn_plot_g)
        right.addWidget(self.btn_plot_out)
        right.addWidget(self.btn_calc_S)
        right.addWidget(self.btn_calc_r)
        right.addWidget(self.button_formulas)
        right.addStretch()
        right.addWidget(self.btn_exit)

        main = QHBoxLayout(self)
        main.addLayout(left, 4)
        main.addLayout(right, 1)

    def read_and_append(self):
        """
        Снимаем Uin и Iout, проверяем, совпадает ли Uin с header текущей колонки,
        и при совпадении записываем Iout в (current_row,current_col).
        """
        try:
            u_in, u_out, i_out = self.controller.get_voltage_current()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось снять данные: {e}")
            return

        col = self.current_col
        max_col = self.table.columnCount()

        # 1) Считаем ожидаемое Usi из заголовка этой колонки
        hdr_item = self.table.horizontalHeaderItem(col)
        try:
            expected_u = float(hdr_item.text())
        except Exception:
            QMessageBox.warning(self, "Неправильный заголовок",
                                f"Невалидный header в колонке {col}")
            return

        # 2) Сверяем с тем, что вернулось из стенда
        if abs(expected_u - u_in) > 1e-3:  # допустим дельта 1 мВ
            QMessageBox.warning(
                self, "Несоответствие напряжения",
                f"Ожидалось Uси = {expected_u:.3f} В, а снято {u_in:.3f} В.\n"
                "Проверьте установку на стенде."
            )
            return

        # 3) Записываем Iк (i_out) в таблицу
        if col < max_col:
            item = QTableWidgetItem(f"{i_out:.3f}")
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(self.current_row, col, item)
        else:
            QMessageBox.warning(self, "Переполнение",
                                "Все колонки для Ic заполнены.")
            return

        # 4) Сдвигаем указатель: вправо, или — если это был последний столбец —
        #    на новую строку и в первую колонку данных
        self.current_col += 1
        if self.current_col >= max_col:
            self.current_col = 2
            self.current_row += 1
            if self.current_row >= self.table.rowCount():
                QMessageBox.information(self, "Готово", "Все строки заполнены.")
                self.btn_read.setEnabled(False)

    def plot_gate(self):

        # 1) X-координаты: ручные Uзи из столбца 0, строки 0–4
        Uzi = []
        for row in range(5):
            it = self.table.item(row, 0)
            try:
                Uzi.append(float(it.text()))
            except Exception:
                Uzi.append(None)

        # 2) Нужные значения Uси
        wanted = {"0.1", "2", "5", "8"}

        # 3) Для каждого столбца 2…N фильтруем по заголовку
        for col in range(2, self.table.columnCount()):
            hdr = self.table.horizontalHeaderItem(col).text()
            if hdr not in wanted:
                continue
            Usi = float(hdr)

            # собираем Ic по этой колонке
            Ic = []
            for row in range(5):
                it = self.table.item(row, col)
                try:
                    Ic.append(float(it.text()))
                except Exception:
                    Ic.append(None)

            # фильтруем пары
            x = [u for u, i in zip(Uzi, Ic) if u is not None and i is not None]
            y = [i for u, i in zip(Uzi, Ic) if u is not None and i is not None]

            if len(x) >= 2:
                plt.plot(x, y, marker='o', linestyle='-', label=f"Uси={Usi:.1f} В")

        plt.xlabel("Uзи, В")
        plt.ylabel("Ic, мА")
        plt.title("Стокозатворная характеристика (выборочные Uси)")
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        plt.show()

    def plot_output(self):

        # 1) Прочитаем массив Uси (из хедеров колонок 2…N)
        Usi = []
        for col in range(2, self.table.columnCount()):
            hdr = self.table.horizontalHeaderItem(col).text()
            try:
                Usi.append(float(hdr))
            except ValueError:
                Usi.append(None)

        # 2) Для каждой строки-данных (rows 1…5) строим свою ветку Ic = f(Usi)
        for row in range(0, self.table.rowCount()):
            # 2a) получаем Uзи из колонки 0
            it_uzi = self.table.item(row, 0)
            if not it_uzi or not it_uzi.text():
                continue
            try:
                Uzi = float(it_uzi.text())
            except ValueError:
                continue

            # 2b) собираем пары (Usi, Ic) для этой строки
            xs, ys = [], []
            for idx, col in enumerate(range(2, self.table.columnCount())):
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

            # 2c) рисуем, если есть хотя бы две точки
            if len(xs) >= 2:
                plt.plot(xs, ys, marker='o', linestyle='-',
                         label=f"Uзи = {Uzi:.2f} В")

        # 3) Оформление и вывод
        plt.xlabel("Uси, В")
        plt.ylabel("Ic, мА")
        plt.title("Выходная характеристика полевого транзистора")
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        plt.show()

    def calc_S(self):
        import matplotlib.pyplot as plt
        from PyQt6.QtWidgets import QMessageBox

        # 1) индексы «измерительных» строк: row 0…4 (Uзи = 3.77, 3.73, 3.65, 3.58, 3.49)
        meas_rows = list(range(0, 5))

        results = {}  # Uси → список S для соседних пар

        # 2) пробегаем по всем столбцам с Uси (колонки 2…end)
        for col in range(2, self.table.columnCount()):
            hdr = self.table.horizontalHeaderItem(col).text()
            try:
                Usi = float(hdr)
            except ValueError:
                continue

            S_list = []
            # 3) для каждой соседней пары строк вычисляем S = ΔIc/ΔUzi
            for i in range(len(meas_rows) - 1):
                r1, r2 = meas_rows[i], meas_rows[i+1]
                item_ic1 = self.table.item(r1, col)
                item_ic2 = self.table.item(r2, col)
                item_u1  = self.table.item(r1, 0)
                item_u2  = self.table.item(r2, 0)
                # пропускаем, если чего-то нет
                if not all([item_ic1, item_ic2, item_u1, item_u2]):
                    continue
                try:
                    Ic1 = float(item_ic1.text())
                    Ic2 = float(item_ic2.text())
                    U1  = float(item_u1.text())
                    U2  = float(item_u2.text())
                except ValueError:
                    continue
                dI = Ic2 - Ic1
                dU = U2 - U1
                if abs(dU) < 1e-9:
                    continue
                S_list.append(dI / dU)

            if S_list:
                results[Usi] = S_list

        # 4) Выводим в окно
        if not results:
            QMessageBox.information(self, "Расчет S", "Нет достаточных данных для расчёта.")
            return

        lines = []
        for Usi, S_vals in results.items():
            seq = ", ".join(f"{s:.3f}" for s in S_vals)
            lines.append(f"Uси={Usi:.2f} В → S = [{seq}] мА/В")
        QMessageBox.information(self, "Крутизна S", "\n".join(lines))

    def calc_resistance(self):
        from PyQt6.QtWidgets import QMessageBox

        try:
            # 1) Собираем мапу header→col
            hdr_to_col = {
                self.table.horizontalHeaderItem(c).text(): c
                for c in range(2, self.table.columnCount())
            }

            # 2) Проверяем наличие нужных колонок
            needed_ohm = ["0.1", "0.5"]  # точки для омического
            needed_dyn = ["6", "9"]      # точки для динамического
            missing = [h for h in (needed_ohm + needed_dyn) if h not in hdr_to_col]
            if missing:
                QMessageBox.warning(
                    self, "Недостаток столбцов",
                    f"Не найдены столбцы: {', '.join(missing)}"
                )
                return

            # 3) Собираем результаты
            results = []
            for row in range(0, 5):  # только экспериментальные строки Uзи
                it_uzi = self.table.item(row, 0)
                if not it_uzi or not it_uzi.text():
                    continue
                Uzi = float(it_uzi.text())

                # --- Омическое R: (0.5−0.1) / (I0.5 − I0.1) ---
                c_lo, c_hi = hdr_to_col["0.1"], hdr_to_col["0.5"]
                i_lo_item = self.table.item(row, c_lo)
                i_hi_item = self.table.item(row, c_hi)
                I_lo = float(i_lo_item.text()) if i_lo_item and i_lo_item.text() else None
                I_hi = float(i_hi_item.text()) if i_hi_item and i_hi_item.text() else None

                if I_lo is None or I_hi is None or abs(I_hi - I_lo) < 1e-9:
                    R_ohm = None
                else:
                    R_ohm = (0.5 - 0.1) / ((I_hi - I_lo) / 1000)

                # --- Динамическое R: (9−6) / (I9 − I6) ---
                c6, c9 = hdr_to_col["6"], hdr_to_col["9"]
                i6_item = self.table.item(row, c6)
                i9_item = self.table.item(row, c9)
                I6 = float(i6_item.text()) if i6_item and i6_item.text() else None
                I9 = float(i9_item.text()) if i9_item and i9_item.text() else None

                if I6 is None or I9 is None or abs(I9 - I6) < 1e-9:
                    R_dyn = None
                else:
                    R_dyn = (9.0 - 6.0) / ((I9 - I6) / 1000)

                results.append((Uzi, R_ohm, R_dyn))

            # 4) Вывод
            if not results:
                QMessageBox.information(self, "Расчёт сопротивлений",
                                        "Нет достаточных данных для расчёта.")
                return

            text = ""
            for Uzi, Rohm, Rdyn in results:
                s_ohm = f"{Rohm:.2f} Ω" if Rohm is not None else "n/a"
                s_dyn = f"{Rdyn:.2f} Ω" if Rdyn is not None else "n/a"
                text += f"Uзи={Uzi:.2f} В: Rₒм={s_ohm}, R_дин={s_dyn}\n"

            QMessageBox.information(self, "Сопротивления", text.rstrip())

        except Exception as e:
            QMessageBox.critical(self, "Ошибка расчёта", str(e))

    def show_formulas(self):
        self.formulas_window.show()