# -*- coding: utf-8 -*-
"""
Table utilities for Hypsometric Curve plugin
Qt6 + modular architecture
"""

import csv
import numpy as np

from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import (
    QTableWidgetItem,
    QMessageBox,
    QFileDialog,
)
from qgis.PyQt.QtCore import (
    QCoreApplication, QSettings, QTranslator, QProcess
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

    # ------------------------------------------------------------------ #
    # POPULATE TABLE
    # ------------------------------------------------------------------ #

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
        """
        Fill table with hypsometric values.
        """

        num_rows = len(intervals) - 1
        table.setRowCount(num_rows)

        # Compute cumulative h and h/H
        h_intervals = intervals[1:] - intervals[:-1]
        h_cum = np.cumsum(h_intervals)
        h_tot = h_cum[-1]

        # Compute hmed for each interval
        valid = data[mask]
        hmed = []
        for i in range(num_rows):
            lower = intervals[i]
            upper = intervals[i + 1]
            vals = valid[(valid >= lower) & (valid < upper)]
            hmed.append(vals.mean() if vals.size > 0 else 0)

        # Fill table
        for i in range(num_rows):
            interval_label = f"{intervals[i]:.2f}-{intervals[i+1]:.2f}"
            a_area = partial_areas[i]
            a_cum = cumulative_areas[i]
            a_norm = a_cum / total_area if total_area > 0 else 0
            h_norm = h_cum[i] / h_tot if h_tot > 0 else 0

            table.setItem(i, 0, QTableWidgetItem(interval_label))
            table.setItem(i, 1, QTableWidgetItem(f"{a_area:.2f}"))
            table.setItem(i, 2, QTableWidgetItem(f"{a_cum:.2f}"))
            table.setItem(i, 3, QTableWidgetItem(f"{a_norm:.4f}"))
            table.setItem(i, 4, QTableWidgetItem(f"{h_cum[i]:.2f}"))
            table.setItem(i, 5, QTableWidgetItem(f"{hmed[i]:.2f}"))
            table.setItem(i, 6, QTableWidgetItem(f"{h_norm:.4f}"))

        self.align(table)
        self.resize(table)

    # ------------------------------------------------------------------ #
    # ALIGNMENT
    # ------------------------------------------------------------------ #

    def align(self, table):
        """Align columns: first left, others right."""
        for row in range(table.rowCount()):
            for col in range(table.columnCount()):
                item = table.item(row, col)
                if not item:
                    continue

                if col == 0:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignLeft)
                else:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignRight)

    # ------------------------------------------------------------------ #
    # RESIZE
    # ------------------------------------------------------------------ #

    def resize(self, table):
        """Resize columns to match UI layout."""
        table.setColumnWidth(0, 110)
        table.setColumnWidth(1, 80)
        table.setColumnWidth(2, 100)
        table.setColumnWidth(3, 60)
        table.setColumnWidth(4, 60)
        table.setColumnWidth(5, 60)
        table.setColumnWidth(6, 60)

    # ------------------------------------------------------------------ #
    # RESET
    # ------------------------------------------------------------------ #

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

    # ------------------------------------------------------------------ #
    # SAVE TABLE
    # ------------------------------------------------------------------ #

    def save_table(self, dlg):
        """Save table to CSV with configurable decimal separator."""

        table = dlg.tableWidget_tabella

        if table.rowCount() == 0:
            QMessageBox.warning(
                dlg, 
                QCoreApplication.translate("HypsometricCurve", "Attenzione"), 
                QCoreApplication.translate("HypsometricCurve", "La tabella è vuota.")
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
            with open(filename, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f, delimiter=";")
                writer.writerow(
                    [QCoreApplication.translate("HypsometricCurve", "Intervalli"),
                     QCoreApplication.translate("HypsometricCurve", "da"), 
                     QCoreApplication.translate("HypsometricCurve", "a"),
                       "a/A", 
                       "h", 
                       "hmed", 
                       "h/H"]
                       )

                for row in range(table.rowCount()):
                    row_data = []
                    for col in range(table.columnCount()):
                        text = table.item(row, col).text()

                        # Convert numeric values
                        try:
                            num = float(text)
                            text = f"{num:.6f}".replace(".", decimal)
                        except ValueError:
                            pass

                        row_data.append(text)

                    writer.writerow(row_data)

            QMessageBox.information(
                dlg, 
                QCoreApplication.translate("HypsometricCurve", "Salvataggio completato"),
                 QCoreApplication.translate("HypsometricCurve", "Tabella salvata!")
                 )

        except Exception as e:
            QMessageBox.critical(
                dlg, 
                QCoreApplication.translate("HypsometricCurve", "Errore"), 
                QCoreApplication.translate("HypsometricCurve", f"Errore durante il salvataggio: {e}")
            )
