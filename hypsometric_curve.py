# -*- coding: utf-8 -*-
"""
HypsometricCurve – QGIS 4 / Qt6
Plugin entry point (GUI + integration with QGIS).
Scientific logic is delegated to core/ modules.
"""

import os

from qgis.PyQt.QtCore import QCoreApplication, QSettings, QTranslator
from qgis.PyQt.QtGui import QAction, QColor, QIcon
from qgis.PyQt.QtWidgets import QMessageBox

from qgis.core import (
    Qgis,
    QgsProject,
    QgsRasterLayer,
    QgsVectorLayer,
    QgsWkbTypes,
)

from .gui.hypsometric_curve_dialog import HypsometricCurveDialog

# Core modules (optimized)
from .core.raster_utils import RasterProcessor
from .core.calculations import HypsometricCalculator
from .core.graph_utils import GraphManager
from .core.table_utils import TableManager


class HypsometricCurve:
    """Main plugin class (QGIS 4 + Qt6)."""

    def __init__(self, iface):
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)

        # Translation
        locale = QSettings().value("locale/userLocale", "it")[0:2]
        locale_path = os.path.join(
            self.plugin_dir, "resources", "i18n", f"hypsometric_curve_{locale}.qm"
        )
        if os.path.exists(locale_path):
            self.translator = QTranslator()
            if self.translator.load(locale_path):
                QCoreApplication.installTranslator(self.translator)

        self.actions = []
        self.menu = self.tr("&Hypsometric Curve")

        # Dialog instance
        self.dlg = None
        self._signals_connected = False

        # Core modules
        self.raster_proc = RasterProcessor()
        self.calc = HypsometricCalculator()
        self.graph = GraphManager()
        self.table = TableManager()

    # ------------------------------------------------------------------ #
    # Translation helper
    # ------------------------------------------------------------------ #

    def tr(self, message):
        return QCoreApplication.translate("HypsometricCurve", message)

    # ------------------------------------------------------------------ #
    # GUI integration
    # ------------------------------------------------------------------ #

    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None,
    ):
        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip:
            action.setStatusTip(status_tip)
        if whats_this:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.iface.addToolBarIcon(action)
        if add_to_menu:
            self.iface.addPluginToVectorMenu(self.menu, action)

        self.actions.append(action)
        return action

    def initGui(self):
        icon_path = os.path.join(self.plugin_dir, "icon.png")
        self.add_action(
            icon_path,
            text=self.tr("Hypsometric Curve"),
            callback=self.run,
            parent=self.iface.mainWindow(),
        )

    def unload(self):
        for action in self.actions:
            self.iface.removePluginVectorMenu(self.menu, action)
            self.iface.removeToolBarIcon(action)
        self.actions.clear()

    # ------------------------------------------------------------------ #
    # Main execution
    # ------------------------------------------------------------------ #

    def run(self):
        if self.dlg is None:
            self.dlg = HypsometricCurveDialog(self.iface.mainWindow())

            # Imposta colore di default del QgsColorButton
            self.dlg.colorButton.setColor(QColor("#1e90ff"))

            # Connect buttons
            self.dlg.pushButton_calc.clicked.connect(self.calculate)
            self.dlg.pushButton_canc.clicked.connect(self.reset_fields)
            self.dlg.pushButton_salva_tab.clicked.connect(self.check_and_save_table)
            self.dlg.pushButton_salva_graph.clicked.connect(self.check_and_save_graph)
            self.dlg.pushButton_refresh.clicked.connect(self.refresh_graph)
            self.dlg.pushButton_close.clicked.connect(self.close_dialog)
            self.dlg.cmb_dem.currentIndexChanged.connect(self.update_band_list)
            self._signals_connected = True

        # Inizializza grafico vuoto con il colore del QgsColorButton
        self.graph.initialize_graph(self.dlg.graphicsView_grafico, self.dlg)

        self.populate_layers()
        self.dlg.show()
        self.dlg.exec()

    # ------------------------------------------------------------------ #
    # Check table
    # ------------------------------------------------------------------ #
    def check_and_save_table(self):
        dlg = self.dlg
        if dlg.tableWidget_tabella.rowCount() == 0:
            QMessageBox.warning(
                dlg,
                self.tr("Attenzione"),
                self.tr("La tabella è vuota. Esegui prima il calcolo.")
            )
            return

        self.table.save_table(dlg)

    def check_and_save_graph(self):
        dlg = self.dlg
        if dlg.tableWidget_tabella.rowCount() == 0:
            QMessageBox.warning(
                dlg,
                self.tr("Attenzione"),
                self.tr("Il grafico non è disponibile. Esegui prima il calcolo.")
            )
            return

        self.graph.save_graph(dlg)

    # ------------------------------------------------------------------ #
    # UI helpers
    # ------------------------------------------------------------------ #

    def populate_layers(self):
        """Fill DEM, band and polygon combos."""
        self.dlg.cmb_dem.blockSignals(True)
        try:
            self.dlg.cmb_dem.clear()
            for lyr in QgsProject.instance().mapLayers().values():
                if isinstance(lyr, QgsRasterLayer) and lyr.isValid():
                    self.dlg.cmb_dem.addItem(lyr.name(), lyr.id())
        finally:
            self.dlg.cmb_dem.blockSignals(False)

        self.update_band_list()

        self.dlg.cmb_polibac.clear()
        for lyr in QgsProject.instance().mapLayers().values():
            if (
                isinstance(lyr, QgsVectorLayer)
                and lyr.isValid()
                and lyr.geometryType() == QgsWkbTypes.PolygonGeometry
            ):
                self.dlg.cmb_polibac.addItem(lyr.name(), lyr.id())

    def update_band_list(self):
        """Update the DEM band combo when the selected DEM changes."""
        self.dlg.cmb_band.clear()
        raster_id = self.dlg.cmb_dem.currentData()
        raster_layer = QgsProject.instance().mapLayer(raster_id) if raster_id else None

        if isinstance(raster_layer, QgsRasterLayer) and raster_layer.isValid():
            for band in range(1, raster_layer.bandCount() + 1):
                self.dlg.cmb_band.addItem(str(band), band)

    def reset_fields(self):
        # Svuota tabella
        self.dlg.tableWidget_tabella.setRowCount(0)

        # Imposta valori a zero
        self.dlg.lineEdit_hmin.setText("0.00")
        self.dlg.lineEdit_hmax.setText("0.00")
        self.dlg.lineEdit_hmed.setText("0.00")
        self.dlg.lineEdit_HI.setText("0.00")
        self.dlg.lineEdit_A.setText("0.00")

        # Reset grafico
        self.graph.initialize_graph(self.dlg.graphicsView_grafico, self.dlg)


    def close_dialog(self):
        self.dlg.close()

    def refresh_graph(self):
        self.graph.update_graph(self.dlg)

    # ------------------------------------------------------------------ #
    # Main calculation pipeline
    # ------------------------------------------------------------------ #

    def calculate(self):
        """Run the calculation and show a user-friendly QGIS error if needed."""
        try:
            self._calculate_impl()
        except Exception as error:
            if self.dlg is not None:
                self.dlg.progressBar.setValue(0)
                QMessageBox.critical(
                    self.dlg,
                    self.tr("Errore"),
                    self.tr(f"Errore durante il calcolo: {error}"),
                )

    def _calculate_impl(self):
        """Full hypsometric workflow."""
        dlg = self.dlg

        # --- Controllo layer selezionati ---
        if dlg.cmb_dem.currentText() == "" or dlg.cmb_polibac.currentText() == "":
            QMessageBox.warning(
                dlg,
                self.tr("Errore"),
                self.tr("Seleziona un DEM e un poligono prima di procedere.")
            )
            return

        if dlg.cmb_band.currentData() is None:
            QMessageBox.warning(
                dlg,
                self.tr("Errore"),
                self.tr("Seleziona una banda valida del DEM.")
            )
            return

        # Retrieve layers
        raster_id = dlg.cmb_dem.currentData()
        basin_id = dlg.cmb_polibac.currentData()
        band_index = dlg.cmb_band.currentData()

        raster_layer = QgsProject.instance().mapLayer(raster_id) if raster_id else None
        basin_layer = QgsProject.instance().mapLayer(basin_id) if basin_id else None

        if not raster_layer or not basin_layer:
            QMessageBox.warning(dlg, self.tr("Errore"),
                                self.tr("Seleziona un DEM e un poligono validi."))
            return

        # Rasterize basin mask (GDAL, ALL_TOUCHED=TRUE)
        mask, data, cell_area, h_min, h_max = self.raster_proc.prepare_raster_data(
            raster_layer, basin_layer, band_index, dlg.progressBar
        )

        # Compute intervals
        num_classes = dlg.spinBox_classi.value()
        intervals = self.calc.compute_intervals(h_min, h_max, num_classes)

        # Compute areas
        partial_areas, cumulative_areas = self.calc.compute_areas(
            data, mask, intervals, cell_area
        )

        # Compute statistics
        h_med = self.calc.compute_h_med(data, mask)
        hi = self.calc.compute_HI(h_med, h_min, h_max)

        # Update UI
        dlg.lineEdit_hmin.setText(f"{h_min:.2f}")
        dlg.lineEdit_hmax.setText(f"{h_max:.2f}")
        dlg.lineEdit_hmed.setText(f"{h_med:.2f}")
        dlg.lineEdit_A.setText(f"{sum(partial_areas):.2f}")
        dlg.lineEdit_HI.setText(f"{hi:.3f}")

        # Populate table
        self.table.populate(
            dlg.tableWidget_tabella,
            intervals,
            partial_areas,
            cumulative_areas,
            sum(partial_areas),
            data,
            mask,
        )

        # Plot graph
        self.graph.plot_graph(self.dlg, hi)

        dlg.progressBar.setValue(100)
        dlg.progressBar.setValue(0)

