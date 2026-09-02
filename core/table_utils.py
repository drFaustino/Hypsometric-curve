# -*- coding: utf-8 -*-

"""
Table utilities for Hypsometric Curve plugin
Qt6 + modular architecture
"""

import csv

import numpy as np

from qgis.PyQt.QtCore import QCoreApplication, Qt
from qgis.PyQt.QtWidgets import (
    QFileDialog,
    QMessageBox,
    QTableWidgetItem,
)


class TableManager:
    """
    Handles:
    - table population
    - alignment
    - resizing
    - CSV export
    - reset
    """

    def __init__(self):
        self._initialized = True

    def populate(
        self,
        table,
        intervals,
        partial_areas,
        cumulative_areas,
        total_area,
        data,
        mask,
    ):
        """Fill table with hypsometric values."""
        num_rows = len(intervals) - 1
        table.setRowCount(num_rows)

        h_intervals = intervals[1:] - intervals[:-1]
        h_cum = np.cumsum(h_intervals)
        h_tot = float(h_cum[-1]) if len(h_cum) else 0.0

        valid = data[mask]
        if np.ma.isMaskedArray(valid):
            valid = valid.compressed()
        else:
            valid = np.asarray(valid)

        hmed = []
        for i in range(num_rows):
            lower = intervals[i]
            upper = intervals[i + 1]

            # Include the maximum elevation in the last class.
            if i == num_rows - 1:
                vals = valid[(valid >= lower) & (valid <= upper)]
            else:
                vals = valid[(valid >= lower) & (valid < upper)]

            hmed.append(float(vals.mean()) if vals.size > 0 else 0.0)

        for i in range(num_rows):
            interval_label = (
                f"{intervals[i]:.2f}-{intervals[i + 1]:.2f}"
            )
            a_area = float(partial_areas[i])
            a_cum = float(cumulative_areas[i])
            a_norm = a_cum / total_area if total_area > 0 else 0.0
            h_norm = h_cum[i] / h_tot if h_tot > 0 else 0.0

            values = (
                interval_label,
                f"{a_area:.2f}",
                f"{a_cum:.2f}",
                f"{a_norm:.4f}",
                f"{h_cum[i]:.2f}",
                f"{hmed[i]:.2f}",
                f"{h_norm:.4f}",
            )

            for col, value in enumerate(values):
                table.setItem(i, col, QTableWidgetItem(value))

        self.align(table)
        self.resize(table)

    def align(self, table):
        """Align columns: first left, others right."""
        for row in range(table.rowCount()):
            for col in range(table.columnCount()):
                item = table.item(row, col)
                if item is None:
                    continue

                alignment = (
                    Qt.AlignmentFlag.AlignLeft
                    if col == 0
                    else Qt.AlignmentFlag.AlignRight
                )
                item.setTextAlignment(alignment)

    def resize(self, table):
        """Resize columns to match UI layout."""
        widths = (110, 80, 100, 60, 60, 60, 60)
        for index, width in enumerate(widths):
            if index < table.columnCount():
                table.setColumnWidth(index, width)

    def reset(self, dlg):
        """Reset table and numeric fields."""
        table = dlg.tableWidget_tabella
        table.clearContents()
        table.setRowCount(0)

        dlg.lineEdit_hmin.setText("0.00")
        dlg.lineEdit_hmax.setText("0.00")
        dlg.lineEdit_hmed.setText("0.00")
        dlg.lineEdit_A.setText("0.00")
        dlg.lineEdit_HI.setText("0.00")

    def save_table(self, dlg):
        """Save table to CSV with configurable decimal separator."""
        table = dlg.tableWidget_tabella

        if table.rowCount() == 0:
            QMessageBox.warning(
                dlg,
                QCoreApplication.translate("HypsometricCurve", "Attenzione"),
                QCoreApplication.translate(
                    "HypsometricCurve",
                    "La tabella è vuota.",
                ),
            )
            return

        filename, _ = QFileDialog.getSaveFileName(
            dlg,
            QCoreApplication.translate("HypsometricCurve", "Salva tabella"),
            "",
            "CSV (*.csv);;Text (*.txt)",
        )

        if not filename:
            return

        decimal = "." if dlg.cmb_decimal.currentIndex() == 0 else ","

        try:
            with open(
                filename,
                "w",
                newline="",
                encoding="utf-8-sig",
            ) as file:
                writer = csv.writer(file, delimiter=";")

                writer.writerow(
                    [
                        QCoreApplication.translate(
                            "HypsometricCurve", "Intervalli"
                        ),
                        QCoreApplication.translate("HypsometricCurve", "da"),
                        QCoreApplication.translate("HypsometricCurve", "a"),
                        "a/A",
                        "h",
                        "hmed",
                        "h/H",
                    ]
                )

                for row in range(table.rowCount()):
                    row_data = []
                    for col in range(table.columnCount()):
                        item = table.item(row, col)
                        text = item.text() if item is not None else ""

                        try:
                            num = float(text)
                        except (TypeError, ValueError):
                            row_data.append(text)
                        else:
                            row_data.append(
                                f"{num:.6f}".replace(".", decimal)
                            )

                    writer.writerow(row_data)

            QMessageBox.information(
                dlg,
                QCoreApplication.translate(
                    "HypsometricCurve",
                    "Salvataggio completato",
                ),
                QCoreApplication.translate(
                    "HypsometricCurve",
                    "Tabella salvata!",
                ),
            )

        except (OSError, csv.Error) as error:
            QMessageBox.critical(
                dlg,
                QCoreApplication.translate("HypsometricCurve", "Errore"),
                QCoreApplication.translate(
                    "HypsometricCurve",
                    f"Errore durante il salvataggio: {error}",
                ),
            )
