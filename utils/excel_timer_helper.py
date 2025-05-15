import pandas as pd
from datetime import datetime
from typing import Dict
from PyQt6.QtWidgets import QTableWidget

def update_timer_label(start_time: datetime, label) -> None:
    """
    Пересчитывает прошедшее время с start_time и пишет в QLabel.
    """
    delta = datetime.now() - start_time
    total = int(delta.total_seconds())
    h = total // 3600
    m = (total % 3600) // 60
    s = total % 60
    label.setText(f"Время выполнения работы {h:02d}:{m:02d}:{s:02d}")

def save_tables_to_excel(
    tables: Dict[str, QTableWidget],
    filename: str,
    engine: str = "openpyxl"
) -> None:
    """
    Сохраняет все QTableWidget в один .xlsx,
    ключи словаря — имена листов.
    """
    with pd.ExcelWriter(filename, engine=engine) as writer:
        for sheet, table in tables.items():
            # извлекаем заголовки
            headers = [
                table.horizontalHeaderItem(c).text() or ""
                for c in range(table.columnCount())
            ]
            # извлекаем строки
            data = []
            for r in range(table.rowCount()):
                row = []
                for c in range(table.columnCount()):
                    item = table.item(r, c)
                    row.append(item.text() if item else "")
                data.append(row)
            # сохраняем лист
            pd.DataFrame(data, columns=headers).to_excel(
                writer, sheet_name=sheet, index=False
            )