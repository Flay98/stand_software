from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem
from PyQt6.QtGui import QKeyEvent, QKeySequence
import pyperclip


class PasteTableWidget(QTableWidget):
    def keyPressEvent(self, event: QKeyEvent):
        if event.matches(QKeySequence.StandardKey.Paste):
            self.paste_from_clipboard()
        else:
            super().keyPressEvent(event)

    def paste_from_clipboard(self):
        text = pyperclip.paste()
        rows = text.strip().split('\n')
        start_row = self.currentRow()
        start_col = self.currentColumn()

        for r, row_data in enumerate(rows):
            columns = row_data.split('\t')
            for c, cell in enumerate(columns):
                if (start_row + r) < self.rowCount() and (start_col + c) < self.columnCount():
                    self.setItem(start_row + r, start_col + c, QTableWidgetItem(cell.strip()))
