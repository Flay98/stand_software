import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QWidget, QVBoxLayout

from lab1.lab1_window import Lab1Window  # Импорт окна ЛР №1
from lab2.lab2_window import Lab2Window
from lab4.lab4_window import Lab4Window


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Главное меню")
        self.resize(400, 300)

        widget = QWidget()
        layout = QVBoxLayout()

        button_lab1 = QPushButton("Лабораторная работа № 1")
        button_lab2 = QPushButton("Лабораторная работа № 2")
        button_lab4 = QPushButton("Лабораторная работа № 4")
        button_lab8 = QPushButton("Лабораторная работа № 8")
        button_lab9 = QPushButton("Лабораторная работа № 9")
        button_lab1.clicked.connect(self.open_lab1)
        button_lab2.clicked.connect(self.open_lab2)
        button_lab4.clicked.connect(self.open_lab4)
        layout.addWidget(button_lab1)
        layout.addWidget(button_lab2)
        layout.addWidget(button_lab4)
        layout.addWidget(button_lab8)
        layout.addWidget(button_lab9)

        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def open_lab1(self):
        self.lab1_window = Lab1Window()
        self.lab1_window.showMaximized()
        self.close()

    def open_lab2(self):
        self.lab2_window = Lab2Window()
        self.lab2_window.showMaximized()
        self.close()

    def open_lab4(self):
        self.lab4_window = Lab4Window()
        self.lab4_window.showMaximized()
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
