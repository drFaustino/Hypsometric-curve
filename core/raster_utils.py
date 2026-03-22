# -*- coding: utf-8 -*-
"""
Raster utilities for Hypsometric Curve plugin
QGIS 4 + Qt6 + GDAL rasterization (ALL_TOUCHED=TRUE)
"""

import numpy as np
from osgeo import gdal, ogr, osr

from qgis.core import (
    QgsRasterLayer,
    QgsVectorLayer,
    QgsCoordinateTransform,
    QgsProject,
    QgsGeometry,
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
        pass

    # ------------------------------------------------------------------ #
    # MAIN ENTRY POINT
    # ------------------------------------------------------------------ #

    def prepare_raster_data(self, raster_layer, basin_layer, band_index, progress_bar):
        """
        Full pipeline:
        1. Read DEM as NumPy array
        2. Rasterize basin polygon (GDAL, ALL_TOUCHED=TRUE)
        3. Create mask
        4. Extract h_min, h_max, cell_area
        """

        # 1. Read DEM
        data, geotransform, nodata, cell_area = self._read_dem(raster_layer, band_index)

        # 2. Rasterize basin polygon
        mask = self._rasterize_basin(
            raster_layer, basin_layer, data.shape, geotransform, progress_bar
        )

        # 3. Mask NoData
        data = np.ma.masked_equal(data, nodata)

        # 4. Mask outside basin
        data = np.ma.masked_where(~mask, data)

        # 5. Compute min/max
        h_min = float(data.min())
        h_max = float(data.max())

        return mask, data, cell_area, h_min, h_max

    # ------------------------------------------------------------------ #
    # DEM READING
    # ------------------------------------------------------------------ #

    def _read_dem(self, raster_layer: QgsRasterLayer, band_index: int):
        """Reads DEM into NumPy array using GDAL."""

        path = raster_layer.dataProvider().dataSourceUri()
        ds = gdal.Open(path)
        band = ds.GetRasterBand(band_index)

        array = band.ReadAsArray().astype(np.float64)
        nodata = band.GetNoDataValue()
        geotransform = ds.GetGeoTransform()

        # Cell area
        px = abs(geotransform[1])
        py = abs(geotransform[5])
        cell_area = px * py

        return array, geotransform, nodata, cell_area

    # ------------------------------------------------------------------ #
    # BASIN RASTERIZATION (GDAL)
    # ------------------------------------------------------------------ #

    def _rasterize_basin(
        self,
        raster_layer: QgsRasterLayer,
        basin_layer: QgsVectorLayer,
        shape,
        geotransform,
        progress_bar,
    ):
        """
        Rasterizes basin polygon using GDAL (ALL_TOUCHED=TRUE).
        Returns a boolean NumPy mask.
        """

        width, height = shape[1], shape[0]

        # Create in-memory raster
        mem_drv = gdal.GetDriverByName("MEM")
        mask_ds = mem_drv.Create("", width, height, 1, gdal.GDT_Byte)
        mask_ds.SetGeoTransform(geotransform)
        mask_ds.SetProjection(raster_layer.crs().toWkt())

        # Convert polygon to OGR layer
        ogr_driver = ogr.GetDriverByName("Memory")
        ogr_ds = ogr_driver.CreateDataSource("memData")
        ogr_layer = ogr_ds.CreateLayer("poly", None, ogr.wkbPolygon)

        # Add geometry
        feat_def = ogr_layer.GetLayerDefn()
        feat = ogr.Feature(feat_def)

        # Transform geometry to raster CRS
        basin_geom = next(basin_layer.getFeatures()).geometry()
        basin_geom = self._transform_geom_to_raster_crs(basin_geom, basin_layer, raster_layer)

        ogr_geom = ogr.CreateGeometryFromWkt(basin_geom.asWkt())
        feat.SetGeometry(ogr_geom)
        ogr_layer.CreateFeature(feat)

        # Rasterize
        gdal.RasterizeLayer(
            mask_ds,
            [1],
            ogr_layer,
            burn_values=[1],
            options=["ALL_TOUCHED=TRUE"],
        )

        # Read mask
        mask = mask_ds.ReadAsArray().astype(bool)

        # Update progress bar
        progress_bar.setValue(40)

        return mask

    # ------------------------------------------------------------------ #
    # CRS TRANSFORMATION
    # ------------------------------------------------------------------ #

    def _transform_geom_to_raster_crs(self, geom: QgsGeometry, basin_layer, raster_layer):
        """Transforms polygon geometry to raster CRS."""

        basin_crs = basin_layer.crs()
        raster_crs = raster_layer.crs()

        if basin_crs == raster_crs:
            return geom

        transform = QgsCoordinateTransform(basin_crs, raster_crs, QgsProject.instance())
        return geom.transform(transform)