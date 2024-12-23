# -*- coding: utf-8 -*-
"""
/***************************************************************************
 HypsometricCurve
                                 A QGIS plugin
 Calculate and draw the hypsometric curve of a drainage basin starting from a vector layer of contour lines and a vector layer that delimits the basin itself.
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2024-12-17
        git sha              : $Format:%H$
        copyright            : (C) 2024 by Dr. Geol. Faustino Cetraro
        email                : geol-faustino@libero.it
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction

import os
import numpy as np
from qgis.core import QgsRasterLayer, QgsRasterBandStats, QgsProject, QgsUnitTypes
from qgis.core import QgsRectangle
from qgis.core import QgsGeometry, QgsPointXY
from qgis.core import QgsFeature, QgsField, QgsFields, QgsVectorLayer
from qgis.core import QgsWkbTypes

from PyQt5.QtCore import QVariant
from PyQt5.QtWidgets import QFileDialog, QTableWidgetItem
from PyQt5.QtWidgets import QGraphicsScene
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import QProgressBar
from PyQt5.QtCore import Qt

from matplotlib import pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import csv


# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .hypsometric_curve_dialog import HypsometricCurveDialog
import os.path


class HypsometricCurve:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'HypsometricCurve_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Hypsometric Curve')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('HypsometricCurve', message)


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
        parent=None):
        
        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToVectorMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""
        icon_path = os.path.join(self.plugin_dir, 'icon.png')
        self.add_action(icon_path, text=self.tr(u'Hypsometric Curve'), callback=self.run, parent=self.iface.mainWindow())

        # will be set False in run()
        self.first_start = True

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginVectorMenu(
                self.tr(u'&Hypsometric Curve'),
                action)
            self.iface.removeToolBarIcon(action)


    def run(self):
        """Run method that performs all the real work"""
        
        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        if self.first_start == True:
            self.first_start = False
            self.dlg = HypsometricCurveDialog()
        
        self.dlg.progressBar.setValue(0)  # Inizializza la barra di progresso
        
        # UI bindings
        self.dlg.cmb_dem.clear()
        self.dlg.cmb_dem.addItems([layer.name() for layer in QgsProject.instance().mapLayers().values() if isinstance(layer, QgsRasterLayer)])

        self.dlg.cmb_band.clear()
        self.dlg.cmb_band.addItems([str(band + 1) for band in range(self.get_band_count())])

        # Pulisce la combobox prima di caricare nuovi valori
        self.dlg.cmb_polibac.clear()

        # Aggiungi i layer poligonali alla combobox
        self.dlg.cmb_polibac.addItems(
            [layer.name() for layer in QgsProject.instance().mapLayers().values() 
            if isinstance(layer, QgsVectorLayer) and layer.geometryType() == QgsWkbTypes.PolygonGeometry]
        )

        self.dlg.pushButton_calc.clicked.connect(self.calculate_hypsometric_curve)
        self.dlg.pushButton_canc.clicked.connect(self.reset_fields)
        self.dlg.pushButton_salva_tab.clicked.connect(self.save_table)
        self.dlg.pushButton_salva_graph.clicked.connect(self.save_graph)
        self.dlg.pushButton_close.clicked.connect(self.dlg.close)

        #vintervalli min e max classi
        self.dlg.spinBox_classi.setMinimum(10)
        self.dlg.spinBox_classi.setMaximum(500)
        #valore per le classi suggerito
        self.dlg.spinBox_classi.setValue(255)
      
        # Imposta la prima scheda come attiva
        self.dlg.tabWidget.setCurrentIndex(0)

        # Initialize the graph with the default view (axes 0 to 1)
        self.initialize_graph()

        # Ridimensiona le colonne
        self.resize_columns()

        #unita' del csr
        self.update_units_label()

        # show the dialog
        self.dlg.show()
        
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass

    def update_units_label(self):
        """Aggiorna la label con le unita' di misura basate sul CRS del layer DEM."""
        raster_name = self.dlg.cmb_dem.currentText()
        raster_layer = next((layer for layer in QgsProject.instance().mapLayers().values() if layer.name() == raster_name), None)

        if not raster_layer:
            self.iface.messageBar().pushMessage("Error", "Select a valid DEM layer", level=3)
            return
        
        # Verifica se il CRS dei layer e' geografico
        dem_crs = raster_layer.crs()

        # Ottieni l'unita' lineare
        distance_unit = dem_crs.mapUnits()

        if distance_unit == QgsUnitTypes.DistanceMeters:
            self.dlg.label_unity.setText("metri - metri^2")
        elif distance_unit == QgsUnitTypes.DistanceFeet:
            self.dlg.label_unity.setText("piedi - piedi^2")
        else:
            self.dlg.label_unity.setText("in gradi!")


    def get_band_count(self):
        """Get the number of bands in the selected raster layer."""
        raster_name = self.dlg.cmb_dem.currentText()
        raster_layer = next((layer for layer in QgsProject.instance().mapLayers().values() if layer.name() == raster_name), None)
        if raster_layer:
            return raster_layer.bandCount()
        return 0
        
    def calculate_hypsometric_curve(self):
        """Perform hypsometric calculations."""
        #barra di progressione
        self.dlg.progressBar.setValue(0)  # Inizializza la barra di progresso

        # Ripulisci la memoria
        self.clear_memory()

        raster_name = self.dlg.cmb_dem.currentText()
        raster_layer = next((layer for layer in QgsProject.instance().mapLayers().values() if layer.name() == raster_name), None)

        if not raster_layer:
            self.iface.messageBar().pushMessage("Error", "Select a valid DEM layer", level=3)
            return
        
        # Verifica se il CRS dei layer e' geografico
        dem_crs = raster_layer.crs()

        if dem_crs.isGeographic():
            # Mostra un avviso e interrompi il calcolo
            QMessageBox.warning(
                None,
                "Attenzione: CRS Geografico",
                "il layer DEM ha un CRS geografico (coordinate in gradi). "
                "Per il calcolo e' necessario un sistema proiettato, come UTM."
            )
            return

        # Ottieni l'unita' lineare
        distance_unit = dem_crs.mapUnits()

        if distance_unit == QgsUnitTypes.DistanceMeters:
            self.dlg.label_unity.setText("metri - metri^2")
        elif distance_unit == QgsUnitTypes.DistanceFeet:
            self.dlg.label_unity.setText("piedi - piedi^2")
        else:
            self.dlg.label_unity.setText("in gradi!")

        band_index = int(self.dlg.cmb_band.currentText())

        # Ottieni il dataProvider del layer raster
        provider = raster_layer.dataProvider()

        # Usa il dataProvider per ottenere le statistiche della banda
        band_stats = provider.bandStatistics(band_index, QgsRasterBandStats.All)     

        # Estrai i valori di min e max
        h_min = band_stats.minimumValue
        h_max = band_stats.maximumValue

        # Visualizza min e max
        self.dlg.lineEdit_hmin.setText(f"{h_min:.2f}")
        self.dlg.lineEdit_hmax.setText(f"{h_max:.2f}")

        self.dlg.progressBar.setValue(10)  # Inizializza la barra di progresso
        
        # Calcoli delle aree ok
        cell_area = abs(raster_layer.rasterUnitsPerPixelX() * raster_layer.rasterUnitsPerPixelY())

        self.dlg.progressBar.setValue(15)  # Inizializza la barra di progresso

        # Ottieni la dimensione del raster (numero di righe e colonne)
        width = raster_layer.width()
        height = raster_layer.height()

        self.dlg.progressBar.setValue(20)  # Inizializza la barra di progresso

        # Crea un QgsRectangle che rappresenta l'intera area del raster
        extent = raster_layer.extent()
        rect = QgsRectangle(extent.xMinimum(), extent.yMinimum(), extent.xMaximum(), extent.yMaximum())

        self.dlg.progressBar.setValue(25)  # Inizializza la barra di progresso

        # Ottieni il blocco di dati per la banda specificata
        block = provider.block(band_index, rect, width, height)

        self.dlg.progressBar.setValue(30)  # Inizializza la barra di progresso

        # Converti i dati del blocco in un array numpy (prima in bytes, poi in float32)
        data = np.frombuffer(block.data(), dtype=np.float32).reshape((height, width))

        self.dlg.progressBar.setValue(35)  # Inizializza la barra di progresso

        # Crea una maschera per identificare i pixel validi (non NoData)
        valid_mask = ~np.isnan(data)

        self.dlg.progressBar.setValue(40)  # Inizializza la barra di progresso

        # Ottieni il nome del layer del bacino selezionato dalla combobox
        basin_layer_name = self.dlg.cmb_polibac.currentText()

        #Seleziona il layer vettoriale del bacino
        basin_layer = next((layer for layer in QgsProject.instance().mapLayers().values() if layer.name() == basin_layer_name), None)

        self.dlg.progressBar.setValue(45)  # Inizializza la barra di progresso
        
        # Verifica se il layer del bacino e' stato trovato
        if basin_layer is None:
            self.iface.messageBar().pushMessage("Error", "No basin layer found with the selected name", level=3)
            return

        # Verifica se il layer e' un poligono
        if basin_layer.geometryType() != QgsWkbTypes.PolygonGeometry:
            self.iface.messageBar().pushMessage("Error", "Selected layer is not a polygon layer", level=3)
            return

        polygon_crs = basin_layer.crs()

        if polygon_crs.isGeographic():
            # Mostra un avviso e interrompi il calcolo
            QMessageBox.warning(
                None,
                "Attenzione: CRS Geografico",
                "il layer del bacino ha un CRS geografico (coordinate in gradi). "
                "Per il calcolo e' necessario un sistema proiettato, come UTM."
            )
            return
        
        # Controlla se i CRS sono uguali (layer DEM e poligono)
        if dem_crs != polygon_crs:
            QMessageBox.warning(
                None,
                "CRS Non Compatibili",
                "Il CRS del layer DEM e' diverso da quello del layer poligono del bacino. "
                "Assicurati che entrambi i layer abbiano lo stesso CRS."
            )
            return

        # Ottieni la geometria del bacino (si suppone che sia un singolo poligono)
        feature = basin_layer.getFeature(0)  # Assicurati di ottenere una feature valida
        if not feature.isValid():
            self.iface.messageBar().pushMessage("Error", "Invalid feature in basin layer", level=3)
            return

        basin_geom = feature.geometry()

        # Verifica se la geometria del bacino e' valida
        if basin_geom.isEmpty() or not basin_geom.isGeosValid():
            self.iface.messageBar().pushMessage("Error", "Invalid or empty geometry for the basin layer", level=3)
            return

        self.dlg.progressBar.setValue(50)  # Inizializza la barra di progresso
        
        # Crea una maschera usando il poligono del bacino
        mask = np.zeros((height, width), dtype=bool)

        self.dlg.progressBar.setValue(0)  # Inizializza la barra di progresso

        for row in range(height):
            for col in range(width):
                # Ottieni la coordinata del centro della cella
                x = extent.xMinimum() + col * raster_layer.rasterUnitsPerPixelX()
                y = extent.yMaximum() - row * raster_layer.rasterUnitsPerPixelY()
                point = QgsPointXY(x, y)

                # Verifica se il punto e' all'interno del poligono del bacino
                if basin_geom.contains(QgsGeometry.fromPointXY(point)):
                    mask[row, col] = True

            self.dlg.progressBar.setValue( int((row + 1) / height * 100))

        self.dlg.progressBar.setValue(55)  # Inizializza la barra di progresso
        
        # Applica la maschera al blocco di dati
        masked_data = data[mask]

        self.dlg.progressBar.setValue(60)  # Inizializza la barra di progresso
        
        # Conta le celle valide e NoData
        valid_cells = np.count_nonzero(~np.isnan(masked_data))
        # no_data_cells = np.count_nonzero(np.isnan(masked_data))

        self.dlg.progressBar.setValue(65)  # Inizializza la barra di progresso
        
        # Calcola l'area totale usando le celle valide
        total_area = valid_cells * cell_area
        self.dlg.lineEdit_A.setText(f"{total_area:.2f}")  #ok correct

        self.dlg.progressBar.setValue(70)  # Inizializza la barra di progresso

        # Recupera il numero di classi definite dall'utente
        num_classes = self.dlg.spinBox_classi.value()

        # Calcola gli intervalli di elevazione
        intervals = np.linspace(h_min, h_max, num_classes + 1)

        class_areas, cumulative_areas = [], []

        self.dlg.progressBar.setValue(75)  # Inizializza la barra di progresso
        
        # Ottieni le aree cumulative per ciascun intervallo
        cumulative_areas = self.calculate_area_in_range(raster_layer, cell_area, band_index, basin_geom)

        # Verifica che il primo valore delle cumulative aree sia uguale all'area totale
        if total_area != cumulative_areas[0]:
            cumulative_areas[0] = total_area  # Sincronizza il valore per sicurezza

        self.dlg.progressBar.setValue(80)  # Inizializza la barra di progresso

        # Non serve ricalcolare le aree cumulative; possiamo derivarle direttamente da cumulative_areas
        class_areas = [cumulative_areas[i] - cumulative_areas[i + 1] for i in range(len(cumulative_areas) - 1)]
        class_areas.append(cumulative_areas[-1])  # Aggiungi l'ultima area (piu' piccola)      

        self.dlg.progressBar.setValue(85)  # Inizializza la barra di progresso

        # Popola la tabella con gli intervalli, le aree cumulative e totali
        self.populate_table(intervals, cumulative_areas, total_area, h_min, h_max)
    
        self.dlg.progressBar.setValue(90)  # Inizializza la barra di progresso
        
        # Hypsometric index
        h_med = self.calculate_hypsometric_mean(cumulative_areas, intervals, total_area, h_min)
        self.dlg.lineEdit_hmed.setText(f"{h_med:.2f}")
        hi = (h_med - h_min) / (h_max - h_min)
        self.dlg.lineEdit_HI.setText(f"{hi:.3f}")

        self.dlg.progressBar.setValue(95)  # Inizializza la barra di progresso

        # disegna il grafico
        self.plot_graph(cumulative_areas, total_area, h_min, h_max, h_med)

        self.dlg.progressBar.setValue(100)  # Inizializza la barra di progresso
        self.dlg.progressBar.setValue(0)  # Inizializza la barra di progresso
        

    def create_contour_polygon(self, valid_mask, raster_layer):
        """Crea un poligono del contorno basato sui pixel validi."""
        # Trova le coordinate dei pixel validi (i pixel che sono 'True' nella valid_mask)
        valid_coords = np.column_stack(np.where(valid_mask))

        # Ottieni il CRS del progetto corrente
        project_crs = QgsProject.instance().crs()

        points = []
        for coord in valid_coords:
            if len(coord) == 2:  # Verifica che 'coord' abbia 2 valori
                row, col = coord  # Ora valid_coords e' bidimensionale (row, col)
            else:
                continue  # Se 'coord' non ha 2 valori, ignora il ciclo per questo elemento

            # Calcola la posizione x, y nel sistema di riferimento del raster
            x = raster_layer.extent().xMinimum() + col * raster_layer.rasterUnitsPerPixelX()
            y = raster_layer.extent().yMaximum() - row * raster_layer.rasterUnitsPerPixelY()
            point = QgsPointXY(x, y)

            # Trasformare la geometria nel CRS del progetto
            point = point.transform(raster_layer.crs(), project_crs)
            points.append(point)

        if len(points) == 0:
            return None

        # Crea un poligono dal contorno delle coordinate
        contour_polygon = QgsGeometry.fromPolygonXY([points])

        return contour_polygon


    def add_polygon_to_map(self, polygon):
        """Aggiunge il poligono del contorno alla mappa."""
        # Ottieni il CRS del progetto corrente
        project_crs = QgsProject.instance().crs()

        # Crea un layer vettoriale temporaneo per il poligono
        fields = QgsFields()
        fields.append(QgsField("id", QVariant.Int))
        layer = QgsVectorLayer("Polygon?crs=" + project_crs.toWkt(), "Contour Polygon", "memory")
        layer.dataProvider().addAttributes(fields)
        layer.updateFields()

        # Crea una feature con il poligono e aggiungila al layer
        feature = QgsFeature()
        feature.setGeometry(polygon)
        feature.setAttributes([1])  # ID attributo
        layer.dataProvider().addFeature(feature)

        # Aggiungi il layer alla mappa
        QgsProject.instance().addMapLayer(layer)

    def calculate_area_in_range(self, raster_layer, cell_area, band_index, basin_geom):
        """
        Calcola le aree cumulative dei pixel in intervalli di elevazione all'interno del poligono del bacino
        in modo ottimizzato.
        """
        # Ottieni il data provider del layer raster
        provider = raster_layer.dataProvider()

        # Estrai l'estensione del raster
        extent = raster_layer.extent()

        # Ottieni la larghezza e altezza del raster (numero di righe e colonne)
        width = raster_layer.width()
        height = raster_layer.height()

        # Usa il dataProvider per ottenere il blocco di dati per la banda
        rect = QgsRectangle(extent.xMinimum(), extent.yMinimum(), extent.xMaximum(), extent.yMaximum())
        block = provider.block(band_index, rect, width, height)

        # Converti i dati del blocco in un array numpy
        data = np.frombuffer(block.data(), dtype=np.float32).reshape((height, width))

        # Gestisci i valori NaN (NoData) nei dati
        data = np.nan_to_num(data, nan=np.nan)

        # Ottieni le statistiche della banda (minimo e massimo)
        band_stats = provider.bandStatistics(band_index, QgsRasterBandStats.All)
        h_min = band_stats.minimumValue
        h_max = band_stats.maximumValue

        # Ottieni il numero di classi dal widget spinBox_classi
        num_classes = self.dlg.spinBox_classi.value()

        # Calcola gli intervalli di elevazione in base al numero di classi
        intervals = np.linspace(h_min, h_max, num_classes + 1)

        # Crea una maschera globale per il bacino
        mask = np.zeros((height, width), dtype=bool)

        self.dlg.progressBar.setValue(0) #barra di avanzamento

        for row in range(height):
            for col in range(width):
                x = extent.xMinimum() + col * raster_layer.rasterUnitsPerPixelX()
                y = extent.yMaximum() - row * raster_layer.rasterUnitsPerPixelY()
                point = QgsPointXY(x, y)
                if basin_geom.contains(QgsGeometry.fromPointXY(point)):
                    mask[row, col] = True
        
            self.dlg.progressBar.setValue( int((row + 1) / height * 100))

        # Applica la maschera al raster per ottenere solo i pixel validi all'interno del bacino
        valid_data = data[mask]

        # Inizializza lista per aree cumulative
        area_cumulative_list = []

        # Calcola le aree per ciascun intervallo
        cumulative_area = 0

        self.dlg.progressBar.setValue(0) #barra di avanzamento

        for i in range(num_classes):
            lower = intervals[i]
            upper = intervals[i + 1]

            # Crea una maschera per i pixel che rientrano nell'intervallo corrente
            interval_mask = (valid_data >= lower) & (valid_data < upper)

            # Calcola l'area per i pixel nell'intervallo
            area = np.sum(interval_mask) * cell_area

            # Aggiorna l'area cumulativa
            cumulative_area += area
            area_cumulative_list.append(cumulative_area)

            self.dlg.progressBar.setValue( int((i + 1) / num_classes * 100))

        # Inverti l'ordine della lista
        area_cumulative_list = area_cumulative_list[::-1]

        return area_cumulative_list

        
    def calculate_hypsometric_mean(self, cumulative_areas, intervals, total_area, h_min):
        """
        Calcola la media ipsoometrica (altezza media) come definito dalla formula:
        hmed = 1/A_tot * Integrale(0, A_tot) h * dA

        cumulative_areas: Array delle aree cumulate
        intervals: Intervallo di elevazione
        total_area: Area totale del raster
        h_min: Altezza minima
        """
        # Verifica che gli intervalli siano allineati correttamente con le aree cumulative
        if len(intervals) == len(cumulative_areas) + 1:
            intervals = intervals[:-1]  # Rimuovi l'ultimo intervallo se e' in eccesso

        # Inizializza la somma pesata
        weighted_sum = 0.0

        # Calcola la somma pesata
        for i in range(len(intervals) - 1):
            # Calcola l'altezza per l'intervallo (h = intervals[i] - h_min)
            h = intervals[i] - h_min

            # Calcola l'area per l'intervallo (dA = a_cum[i] - a_cum[i+1])
            if i < len(intervals) - 2:
                dA = cumulative_areas[i] - cumulative_areas[i + 1]
            else:
                dA = cumulative_areas[i]  # Ultimo intervallo, l'area e' l'area totale

            # Assicurati che dA non sia negativo (se c'e' qualche errore nei dati)
            if dA < 0:
                dA = 0

            # Somma pesata dell'altezza per l'area dell'intervallo
            weighted_sum += h * dA

        # La media ipsoometrica e' la somma pesata divisa per l'area totale
        if total_area > 0:
            hmed = weighted_sum / total_area
        else:
            hmed = 0  # Nel caso di area totale pari a zero

        return hmed


    def populate_table(self, intervals, cumulative_areas, total_area, h_min, h_max):
        """Fill table with hypsometric data."""
        self.dlg.tableWidget_tabella.setRowCount(len(intervals) - 1)
        for i in range(len(intervals) - 1):
            h = intervals[i] - h_min
            h_h_tot = h / (h_max - h_min)
            a_cum = cumulative_areas[i]
            a_cum_norm = a_cum / total_area
            # d_a = cumulative_areas[i - 1] - a_cum if i > 0 else a_cum - cumulative_areas[i + 1]
            d_a = a_cum - cumulative_areas[i + 1] if i < len(intervals) - 2 else a_cum

            self.dlg.tableWidget_tabella.setItem(i, 0, QTableWidgetItem(f"{intervals[i]:.2f}-{intervals[i + 1]:.2f}"))
            self.dlg.tableWidget_tabella.setItem(i, 1, QTableWidgetItem(f"{a_cum:.2f}"))
            self.dlg.tableWidget_tabella.setItem(i, 2, QTableWidgetItem(f"{a_cum_norm:.4f}"))
            self.dlg.tableWidget_tabella.setItem(i, 3, QTableWidgetItem(f"{d_a:.2f}"))
            self.dlg.tableWidget_tabella.setItem(i, 4, QTableWidgetItem(f"{h:.2f}"))
            self.dlg.tableWidget_tabella.setItem(i, 5, QTableWidgetItem(f"{h_h_tot:.4f}"))
        
        # Allinea le colonne dopo aver scritto i dati nella tabella
        self.align_columns()

        # Ridimensiona le colonne 3 e 6
        self.resize_columns()
  
    def plot_graph(self, cumulative_areas, total_area, h_min, h_max, hypsometric_mean):
        """Plot hypsometric curve."""
        # Normalizza le aree cumulative rispetto all'area totale
        a_norm = [a / total_area for a in cumulative_areas]

        # Calcola gli intervalli normalizzati da h_min a h_max
        h_norm = [(interval - h_min) / (h_max - h_min) for interval in np.linspace(h_min, h_max, len(cumulative_areas))]

         # Create a new figure with the specified size (5.21 x 3.51 inches corresponding to 521x351 pixels)
        fig, ax = plt.subplots(figsize=(5.21, 3.51))
        
         # Plot the hypsometric curve
        ax.plot(a_norm, h_norm, color="blue", label="Curva ipsometrica")
        ax.set_xlabel("Rapporto a/A")
        ax.set_ylabel("Rapporto h/H")
        ax.set_title("Grafico della curva ipsometrica")
        ax.legend()
        ax.grid(True)  # Show the grid
        
        # Set the x and y axis limits from 0 to 1
        ax.set_xlim(0, 1.1)
        ax.set_ylim(0, 1.1)

        # Mostra il punto HI sulla curva se il checkbox e' selezionato
        if self.dlg.checkBox_HI.isChecked():
            # Calcola HI normalizzato
            hi_normalized = hypsometric_mean / (h_max - h_min)  # h/H

            # Trova il punto piu' vicino alla curva ipsometrica
            for i in range(len(h_norm) - 1):
                if h_norm[i] <= hi_normalized <= h_norm[i + 1]:
                    # Interpolazione lineare per trovare il valore esatto di a/A
                    slope = (a_norm[i + 1] - a_norm[i]) / (h_norm[i + 1] - h_norm[i])
                    hi_projection = a_norm[i] + slope * (hi_normalized - h_norm[i])  # a/A
                    break
            
            # Aggiungi le linee tratteggiate proiettate sugli assi
            ax.axhline(hi_normalized, color='green', linestyle='--', linewidth=0.8)
            
            # Disegna un cerchietto sul punto HI sulla curva
            ax.plot([hi_projection], [hi_normalized], 'o', color='red', label="HI")

            # Aggiungi il valore di HI come etichetta
            hi_value = float(self.dlg.lineEdit_HI.text())

            ax.text(
                hi_projection + 0.02,  # Posizione x leggermente a destra del punto
                hi_normalized + 0.02,  # Posizione y leggermente sopra il punto
                f"HI = {hi_value:.3f}",  # Testo con il valore di HI
                color="black",
                fontsize=9,
                fontweight='bold'       # Aggiunge il grassetto al testo
            )          

        # Adjust layout to ensure titles and labels fit within the figure
        plt.tight_layout()

        # Create the FigureCanvas to display the plot in the graphics view
        canvas = FigureCanvas(fig)
        canvas.setFixedSize(521, 351)  # Ensure the canvas fits the graphics view size

        # Clear the previous content and add the new plot to the QGraphicsView
        self.dlg.graphicsView_grafico.setScene(QGraphicsScene())
        self.dlg.graphicsView_grafico.scene().addWidget(canvas)

        # Draw the canvas
        canvas.draw()

    def initialize_graph(self):
        """Initialize the graph with axes from 0 to 1 and show the grid."""
        # Create a figure and axis for the plot
        fig, ax = plt.subplots(figsize=(5.21, 3.51)) # Size in inches, corresponding to 521x351 pixels at 100 dpi
        
        # Set the x and y axis limits from 0 to 1
        ax.set_xlim(0, 1.1)
        ax.set_ylim(0, 1.1)
        
        # Set labels for the axes
        ax.set_xlabel("Rapporto a/A", labelpad=15)
        ax.set_ylabel("Rapporto h/H", labelpad=10)
        ax.set_title("Grafico della curva ipsometrica", pad=20)
        
        # Add a grid
        ax.grid(True)
        
        # Adjust the margins of the plot to make sure labels and title are not cut off
        # plt.subplots_adjust(bottom=0.15, left=0.1, right=0.9, top=0.85)  # Modifica i margini (aumenta bottom, top, left, right)
    
        # Use tight_layout to automatically adjust the subplots to fit the figure area
        plt.tight_layout()  # Ottimizza automaticamente i margini per evitare che vengano tagliati
        
        # Create a canvas for displaying the figure in the graphics view
        canvas = FigureCanvas(fig)

        # Set the canvas size to match the graphics view
        canvas.setFixedSize(521, 351)
        
        # Clear the previous content and add the new plot to the QGraphicsView
        self.dlg.graphicsView_grafico.setScene(QGraphicsScene())
        self.dlg.graphicsView_grafico.scene().addWidget(canvas)
        
        # Draw the canvas
        canvas.draw()

    def reset_fields(self):
        """Reset all input and output fields."""
        self.dlg.lineEdit_hmin.setText("0.00")
        self.dlg.lineEdit_hmax.setText("0.00")
        self.dlg.lineEdit_A.setText("0.00")
        self.dlg.lineEdit_hmed.setText("0.00")
        self.dlg.lineEdit_HI.setText("0.00")

        # Reset the tabel
        self.dlg.tableWidget_tabella.clearContents()  # Svuota il contenuto della tabella
        self.dlg.tableWidget_tabella.setRowCount(0)   # Elimina tutte le righe

        # Reset any stored data related to the computation
        self.cumulative_areas = []
        self.total_area = 0.0
        self.h_min = 0.0
        self.h_max = 0.0
        self.hypsometric_mean = 0.0

        # Reset the graph to the initial state with axes from 0 to 1 and grid
        self.initialize_graph()
    
    def clear_memory(self):
        """Clear internal memory of stored data."""
        self.cumulative_areas = []
        self.total_area = 0.0
        self.h_min = 0.0
        self.h_max = 0.0
        self.hypsometric_mean = 0.0

    def save_table(self):
        """Save table data to a CSV file."""
        table = self.dlg.tableWidget_tabella
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(self.dlg, "Save Table", "", "CSV Files (*.csv);;Text Files (*.txt)")
        
        # Interrompi se l'utente ha premuto "Annulla"
        if not filename:
            return
       
        # Recupero del separatore decimale dalla combobox (0 per punto, 1 per virgola)
        decimal_separator = '.' if self.dlg.cmb_decimal.currentIndex() == 0 else ','

        if filename:
            try:
                with open(filename, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f, delimiter=';')
                    writer.writerow(["Intervalli", "a_cum", "a_cum/A", "dA", "h", "h/H"])
                    
                    for row in range(table.rowCount()):
                        row_data = []
                        for col in range(table.columnCount()):
                            
                            cell_text = table.item(row, col).text()
                            
                            try:
                                # Se il valore e' numerico, convertilo al formato corretto
                                numeric_value = float(cell_text)
                                formatted_value = f"{numeric_value:.6f}".replace('.', decimal_separator)
                                row_data.append(formatted_value)
                            except ValueError:
                                # Se non e' un numero, aggiungi il testo cosi' com'e'
                                row_data.append(cell_text)
                        
                        writer.writerow(row_data)               

                # Mostra un messaggio di conferma
                QtWidgets.QMessageBox.information(self.dlg, "Salvataggio completato", "I dati sono stati salvati correttamente!")
            
            except Exception as e:
                # Se c'e' un errore nel salvataggio, mostra un messaggio di errore
                QtWidgets.QMessageBox.critical(self.dlg, "Errore", f"Si e' verificato un errore durante il salvataggio: {str(e)}")


    def save_graph(self):
        """Save graph to an image file."""
        path, _ = QFileDialog.getSaveFileName(None, "Save Graph", "", "Images (*.png *.jpg)")

        # Interrompi se l'utente ha premuto "Annulla"
        if not path:
            return
        
        if path:
            try:
                plt.savefig(path)
                
                # Mostra un messaggio di conferma
                QMessageBox.information(None, "Salvataggio completato", "Il grafico e' stato salvato correttamente!")
            
            except Exception as e:
                # Mostra un messaggio di errore se c'e' un problema durante il salvataggio
                QMessageBox.critical(None, "Errore", f"Si e' verificato un errore durante il salvataggio del grafico: {str(e)}")
    

    def align_columns(self):
        """Allinea le colonne della tabella come richiesto."""
        table = self.dlg.tableWidget_tabella
        
        # Itera su tutte le righe e le colonne
        for row in range(table.rowCount()):
            for col in range(table.columnCount()):
                item = table.item(row, col)
                if item:
                    # Allinea la prima colonna a sinistra
                    if col == 0:
                        item.setTextAlignment(Qt.AlignLeft)
                    else:
                        # Allinea tutte le altre colonne a destra
                        item.setTextAlignment(Qt.AlignRight)
    
    def resize_columns(self):
        """Ridimensiona le colonne 3 e 6 della tabella a una larghezza di 70."""
        table = self.dlg.tableWidget_tabella
        table.setColumnWidth(2, 60)  # La colonna 3 ha indice 2 (gli indici partono da 0)
        table.setColumnWidth(3, 90)
        table.setColumnWidth(4, 70)
        table.setColumnWidth(5, 60)  # La colonna 6 ha indice 5