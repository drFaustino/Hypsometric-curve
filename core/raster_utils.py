# -*- coding: utf-8 -*-
"""
Raster utilities for Hypsometric Curve plugin
QGIS 4 + Qt6 + GDAL rasterization (ALL_TOUCHED=TRUE)
"""

import numpy as np
from osgeo import gdal, ogr

from qgis.core import (
    Qgis,
    QgsCoordinateTransform,
    QgsGeometry,
    QgsProject,
    QgsRasterLayer,
    QgsVectorLayer,
)


class RasterProcessor:
    """
    Handles:
    - DEM reading
    - GDAL rasterization of basin polygon
    - mask creation
    - extraction of raster values as NumPy arrays
    """

    def __init__(self):
        self._initialized = True

    def prepare_raster_data(
        self,
        raster_layer,
        basin_layer,
        band_index,
        progress_bar,
    ):
        """
        Read the DEM, rasterize the basin and calculate
        the minimum and maximum elevation.
        """
        if not isinstance(raster_layer, QgsRasterLayer) or not raster_layer.isValid():
            raise RuntimeError("Il layer DEM non è valido.")

        if not isinstance(basin_layer, QgsVectorLayer) or not basin_layer.isValid():
            raise RuntimeError("Il layer del bacino non è valido.")

        band_index = int(band_index)
        if band_index < 1 or band_index > raster_layer.bandCount():
            raise RuntimeError("La banda raster selezionata non è valida.")

        data, geotransform, nodata, cell_area = self._read_dem(
            raster_layer,
            band_index,
        )

        if progress_bar is not None:
            progress_bar.setValue(20)

        mask = self._rasterize_basin(
            raster_layer,
            basin_layer,
            data.shape,
            geotransform,
            progress_bar,
        )

        if nodata is not None:
            data = np.ma.masked_equal(data, nodata)

        data = np.ma.masked_where(~mask, data)

        if data.count() == 0:
            raise RuntimeError(
                "Il bacino non contiene valori validi del DEM."
            )

        h_min = float(data.min())
        h_max = float(data.max())

        return mask, data, cell_area, h_min, h_max

    def _read_dem(
        self,
        raster_layer: QgsRasterLayer,
        band_index: int,
    ):
        """Read a DEM band into a NumPy array."""
        path = raster_layer.source()
        dataset = gdal.Open(path)

        if dataset is None:
            # Some providers expose a URI rather than a plain source path.
            path = raster_layer.dataProvider().dataSourceUri()
            dataset = gdal.Open(path)

        if dataset is None:
            raise RuntimeError(
                "Impossibile aprire il raster DEM con GDAL."
            )

        try:
            band = dataset.GetRasterBand(band_index)

            if band is None:
                raise RuntimeError(
                    f"Impossibile leggere la banda raster {band_index}."
                )

            array = band.ReadAsArray()

            if array is None:
                raise RuntimeError(
                    "Impossibile leggere i dati del raster DEM."
                )

            array = np.asarray(array, dtype=np.float64)
            nodata = band.GetNoDataValue()
            geotransform = dataset.GetGeoTransform()

            if geotransform is None:
                raise RuntimeError(
                    "Il raster DEM non contiene una geotransform valida."
                )

            px = abs(float(geotransform[1]))
            py = abs(float(geotransform[5]))
            cell_area = px * py

            if cell_area <= 0:
                raise RuntimeError(
                    "La dimensione della cella del DEM non è valida."
                )

            return array, geotransform, nodata, cell_area
        finally:
            dataset = None

    def _unwrap_geom(self, geom):
        """Return a QgsGeometry from a geometry-operation result when needed."""
        if isinstance(geom, QgsGeometry):
            return geom

        if hasattr(geom, "geometry"):
            candidate = geom.geometry()
            if isinstance(candidate, QgsGeometry):
                return candidate

        return geom

    def _rasterize_basin(
        self,
        raster_layer: QgsRasterLayer,
        basin_layer: QgsVectorLayer,
        shape,
        geotransform,
        progress_bar,
    ):
        """Rasterize all basin polygon features using GDAL."""
        width = int(shape[1])
        height = int(shape[0])

        mem_driver = gdal.GetDriverByName("MEM")
        if mem_driver is None:
            raise RuntimeError("Driver GDAL MEM non disponibile.")

        mask_ds = mem_driver.Create(
            "",
            width,
            height,
            1,
            gdal.GDT_Byte,
        )
        if mask_ds is None:
            raise RuntimeError("Impossibile creare il raster temporaneo.")

        try:
            mask_ds.SetGeoTransform(geotransform)
            mask_ds.SetProjection(raster_layer.crs().toWkt())

            ogr_driver = ogr.GetDriverByName("Memory")
            if ogr_driver is None:
                raise RuntimeError("Driver OGR Memory non disponibile.")

            ogr_ds = ogr_driver.CreateDataSource("memData")
            if ogr_ds is None:
                raise RuntimeError("Impossibile creare il datasource OGR.")

            try:
                ogr_layer = ogr_ds.CreateLayer(
                    "poly",
                    None,
                    ogr.wkbUnknown,
                )
                if ogr_layer is None:
                    raise RuntimeError(
                        "Impossibile creare il layer OGR temporaneo."
                    )

                feature_count = 0
                for basin_feature in basin_layer.getFeatures():
                    basin_geom = basin_feature.geometry()
                    if basin_geom is None or basin_geom.isEmpty():
                        continue

                    basin_geom = self._transform_geom_to_raster_crs(
                        basin_geom,
                        basin_layer,
                        raster_layer,
                    )
                    basin_geom = self._unwrap_geom(basin_geom)

                    if basin_geom is None or basin_geom.isEmpty():
                        continue

                    ogr_geom = ogr.CreateGeometryFromWkt(
                        basin_geom.asWkt()
                    )
                    if ogr_geom is None:
                        continue

                    feature_definition = ogr_layer.GetLayerDefn()
                    feature = ogr.Feature(feature_definition)
                    try:
                        feature.SetGeometry(ogr_geom)
                        ogr_layer.CreateFeature(feature)
                        feature_count += 1
                    finally:
                        feature = None
                        ogr_geom = None

                if feature_count == 0:
                    raise RuntimeError(
                        "Il layer del bacino non contiene geometrie valide."
                    )

                result = gdal.RasterizeLayer(
                    mask_ds,
                    [1],
                    ogr_layer,
                    burn_values=[1],
                    options=["ALL_TOUCHED=TRUE"],
                )

                if result != 0:
                    raise RuntimeError(
                        "Errore durante la rasterizzazione del bacino."
                    )

                mask_array = mask_ds.ReadAsArray()
                if mask_array is None:
                    raise RuntimeError(
                        "Impossibile leggere la maschera raster."
                    )

                mask = np.asarray(mask_array, dtype=bool)

                if progress_bar is not None:
                    progress_bar.setValue(40)

                return mask
            finally:
                ogr_ds = None
        finally:
            mask_ds = None

    def _transform_geom_to_raster_crs(
        self,
        geom,
        basin_layer,
        raster_layer,
    ):
        """Transform a copy of the basin geometry to the raster CRS."""
        basin_crs = basin_layer.crs()
        raster_crs = raster_layer.crs()

        if basin_crs == raster_crs:
            return QgsGeometry(geom)

        transform = QgsCoordinateTransform(
            basin_crs,
            raster_crs,
            QgsProject.instance(),
        )

        transformed = QgsGeometry(geom)
        result = transformed.transform(transform)

        # In QGIS 4 transform() changes the geometry in place and returns
        # a GeometryOperationResult. Keep the copy when the operation succeeds.
        if result is not None and result != Qgis.GeometryOperationResult.Success:
            raise RuntimeError(
                "Impossibile trasformare la geometria del bacino nel CRS del DEM."
            )

        return transformed
