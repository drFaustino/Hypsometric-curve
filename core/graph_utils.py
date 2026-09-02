# -*- coding: utf-8 -*-
"""
Graph utilities for Hypsometric Curve plugin
Qt6 + Matplotlib + QGraphicsView
"""

import numpy as np
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas

from qgis.PyQt.QtWidgets import QGraphicsScene
from qgis.PyQt.QtCore import QCoreApplication


class GraphManager:
    """
    Handles:
    - initialization of empty graph
    - plotting hypsometric curve
    - projecting HI on the curve
    """

    def __init__(self):
        self._figure = None
        self._canvas = None

    # ------------------------------------------------------------------ #
    # INITIAL EMPTY GRAPH
    # ------------------------------------------------------------------ #
    def initialize_graph(self, graphics_view, dlg):
        """Draws an empty graph with axes 0–1."""

        W, H = 531, 361
        DPI = 96

        fig, ax = plt.subplots(figsize=(W / DPI, H / DPI), dpi=DPI)

        # Use QgsColorButton color
        ax.set_prop_cycle(color=[dlg.colorButton.color().name()])

        ax.set_xlim(0, 1.1)
        ax.set_ylim(0, 1.1)
        ax.set_xlabel("a/A", fontweight="bold")
        ax.set_ylabel("h/H", fontweight="bold")
        ax.set_title(
            QCoreApplication.translate("HypsometricCurve", "Curva ipsometrica"),
            fontweight="bold",
        )
        ax.grid(True)

        fig.tight_layout(pad=0.5)

        canvas = FigureCanvas(fig)
        canvas.setFixedSize(W, H)
        self._figure = fig
        self._canvas = canvas

        scene = QGraphicsScene()
        scene.addWidget(canvas)
        graphics_view.setScene(scene)
        canvas.draw()

    # ------------------------------------------------------------------ #
    # MAIN PLOT
    # ------------------------------------------------------------------ #
    def plot_graph(self, dlg, hi):
        """Plot hypsometric curve using table values."""

        table = dlg.tableWidget_tabella
        rows = table.rowCount()

        a_norm = np.array([float(table.item(i, 3).text()) for i in range(rows)])
        h_norm = np.array([float(table.item(i, 6).text()) for i in range(rows)])

        W, H = 531, 361
        DPI = 96

        fig, ax = plt.subplots(figsize=(W / DPI, H / DPI), dpi=DPI)

        # Use QgsColorButton color
        color = dlg.colorButton.color().name()

        ax.plot(
            a_norm,
            h_norm,
            color=color,  # <<< QUI la correzione: usiamo la variabile color
            linewidth=1.8,
            label=QCoreApplication.translate("HypsometricCurve", "Curva ipsometrica"),
        )

        ax.set_xlim(0, 1.1)
        ax.set_ylim(0, 1.1)
        ax.set_xlabel("a/A", fontweight="bold")
        ax.set_ylabel("h/H", fontweight="bold")
        ax.set_title(
            QCoreApplication.translate("HypsometricCurve", "Curva ipsometrica"),
            fontweight="bold",
        )
        ax.grid(True)
        ax.legend()

        if dlg.checkBox_HI.isChecked():
            self._plot_HI_projection(ax, a_norm, h_norm, hi)

        fig.tight_layout(pad=0.5)

        canvas = FigureCanvas(fig)
        canvas.setFixedSize(W, H)
        self._figure = fig
        self._canvas = canvas

        scene = QGraphicsScene()
        scene.addWidget(canvas)
        dlg.graphicsView_grafico.setScene(scene)
        canvas.draw()

    # ------------------------------------------------------------------ #
    # HI PROJECTION
    # ------------------------------------------------------------------ #
    def _plot_HI_projection(self, ax, a_norm, h_norm, hi):
        hi_projection = None
        for i in range(len(h_norm) - 1):
            if h_norm[i] <= hi <= h_norm[i + 1]:
                slope = (a_norm[i + 1] - a_norm[i]) / (h_norm[i + 1] - h_norm[i])
                hi_projection = a_norm[i] + slope * (hi - h_norm[i])
                break

        if hi_projection is None:
            return

        ax.axhline(hi, color="green", linestyle="--", linewidth=0.8)
        ax.plot([hi_projection], [hi], "o", color="red")
        ax.text(
            hi_projection + 0.02,
            hi + 0.02,
            f"HI = {hi:.3f}",
            fontsize=9,
            fontweight="bold",
            color="black",
        )

    # ------------------------------------------------------------------ #
    # UPDATE GRAPH COLOR
    # ------------------------------------------------------------------ #
    def update_graph(self, dlg):
        try:
            hi = float(dlg.lineEdit_HI.text())
        except (TypeError, ValueError):
            hi = 0.0
        self.plot_graph(dlg, hi)

    # ------------------------------------------------------------------ #
    # SAVE GRAPH
    # ------------------------------------------------------------------ #
    def save_graph(self, dlg):
        import matplotlib.pyplot as plt
        from qgis.PyQt.QtWidgets import QFileDialog, QMessageBox

        path, _ = QFileDialog.getSaveFileName(
            dlg,
            QCoreApplication.translate("HypsometricCurve", "Salva grafico"),
            "",
            "Images (*.png *.jpg)",
        )
        if not path:
            return

        try:
            if self._figure is None:
                raise RuntimeError("Grafico non disponibile.")
            self._figure.savefig(path, bbox_inches="tight")
            QMessageBox.information(
                dlg,
                QCoreApplication.translate("HypsometricCurve", "Salvataggio completato"),
                QCoreApplication.translate("HypsometricCurve", "Grafico salvato!"),
            )
        except Exception as e:
            QMessageBox.critical(
                dlg,
                QCoreApplication.translate("HypsometricCurve", "Errore"),
                QCoreApplication.translate(
                    "HypsometricCurve", f"Errore durante il salvataggio: {e}"
                ),
            )
