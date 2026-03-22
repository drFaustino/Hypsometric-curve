# -*- coding: utf-8 -*-
"""
HypsometricCurve – QGIS 4 / Qt6
Plugin entry point (GUI + integration with QGIS).
Scientific logic is delegated to core/ modules.
"""

import os

from qgis.PyQt.QtCore import QCoreApplication, QSettings, QTranslator
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QMessageBox

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
        """Open dialog and initialize UI."""
        if self.dlg is None:
            self.dlg = HypsometricCurveDialog(self.iface.mainWindow())

            # Connect buttons
            self.dlg.pushButton_calc.clicked.connect(self.calculate)
            self.dlg.pushButton_canc.clicked.connect(self.reset_fields)

            self.dlg.pushButton_salva_tab.clicked.connect(
                lambda: self.table.save_table(self.dlg)
            )
            self.dlg.pushButton_salva_graph.clicked.connect(
                lambda: self.graph.save_graph(self.dlg)
            )

            self.dlg.pushButton_refresh.clicked.connect(self.refresh_graph)
            self.dlg.pushButton_close.clicked.connect(self.close_dialog)
            self.dlg.pushButton_color.clicked.connect(
                lambda: self.graph.select_color(self.dlg)
            )       

        self.populate_layers()
        self.graph.initialize_graph(self.dlg.graphicsView_grafico)

        self.dlg.show()
        self.dlg.exec()

    # ------------------------------------------------------------------ #
    # UI helpers
    # ------------------------------------------------------------------ #

    def populate_layers(self):
        """Fill DEM, band and polygon combos."""
        self.dlg.cmb_dem.clear()
        dem_layers = [
            lyr.name()
            for lyr in QgsProject.instance().mapLayers().values()
            if isinstance(lyr, QgsRasterLayer)
        ]
        self.dlg.cmb_dem.addItems(dem_layers)

        # Bands
        self.dlg.cmb_band.clear()
        raster_name = self.dlg.cmb_dem.currentText()
        raster_layer = next(
            (lyr for lyr in QgsProject.instance().mapLayers().values()
             if lyr.name() == raster_name),
            None,
        )
        if raster_layer:
            for band in range(raster_layer.bandCount()):
                self.dlg.cmb_band.addItem(str(band + 1), band + 1)

        # Polygons
        self.dlg.cmb_polibac.clear()
        poly_layers = [
            lyr.name()
            for lyr in QgsProject.instance().mapLayers().values()
            if isinstance(lyr, QgsVectorLayer)
            and lyr.geometryType() == QgsWkbTypes.PolygonGeometry
        ]
        self.dlg.cmb_polibac.addItems(poly_layers)

    def reset_fields(self):
        self.table.reset(self.dlg)
        self.graph.initialize_graph(self.dlg.graphicsView_grafico)
        self.dlg.progressBar.setValue(0)

    def close_dialog(self):
        self.dlg.close()

    def refresh_graph(self):
        self.graph.update_graph(self.dlg)

    # ------------------------------------------------------------------ #
    # Main calculation pipeline
    # ------------------------------------------------------------------ #

    def calculate(self):
        """Full hypsometric workflow."""
        dlg = self.dlg

        # Retrieve layers
        raster_name = dlg.cmb_dem.currentText()
        basin_name = dlg.cmb_polibac.currentText()
        band_index = dlg.cmb_band.currentData()

        raster_layer = next(
            (lyr for lyr in QgsProject.instance().mapLayers().values()
             if lyr.name() == raster_name),
            None,
        )
        basin_layer = next(
            (lyr for lyr in QgsProject.instance().mapLayers().values()
             if lyr.name() == basin_name),
            None,
        )

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
        hi = self.calc.compute_HI(intervals, h_min, h_max)

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
        self.graph.plot_graph(dlg, hi)

        dlg.progressBar.setValue(100)
        dlg.progressBar.setValue(0)   # retun to zero

