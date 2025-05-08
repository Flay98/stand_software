from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtGui import QPixmap
import os


class FormulasWindow(QWidget):
    def __init__(self, lab_number: int = 1):
        super().__init__()
        self.setWindowTitle(f"Формулы для Лабораторной №{lab_number}")
        self.resize(600, 600)

        layout = QVBoxLayout()
        label = QLabel()

        image_filename = f"formulas_lab{lab_number}.png"
        image_path = os.path.join(os.path.dirname(__file__), "formulas", image_filename)

        pixmap = QPixmap(image_path)
        if pixmap.isNull():
            label.setText(f"Не удалось загрузить изображение: {image_filename}")
        else:
            label.setPixmap(pixmap)
            label.setScaledContents(True)

        layout.addWidget(label)
        self.setLayout(layout)
