# Hypsometric curve
## QGIS plugin
### Update version 0.5, minimum required QGIS v. 3.x

Calculates the **hypsometric curve** of a drainage basin from a terrain DEM layer and the definition of the perimeter of the basin, obtained from a vector layer containing the polygon that delimits its boundaries. It is possible to choose the number of bands for the terrain elevations and define the number of classes of the elevation intervals to divide the area of ​​the basin itself. As a result, the minimum, maximum and average elevation inside the basin polygon, the total area and the value of the hypsometric integral are calculated. In addition, the graph of the hypsometric curve is drawn, with the relative calculated values ​​reported in a table. It is possible to save both the graph in image format and the table of values ​​in a CSV or TXT file.

The plugin requires the use of the **numpy**, **matplotlib**, **pyplot** and **csv** libraries.

## Update

In the improved version, a new calculation mode for hmed and HI has been introduced. Additional controls have been added on the raster layer and new fields have been implemented in the table to display additional information. Float32 and Float64 data are now supported. Additionally, the interface has been remodeled to accommodate the new elements inserted. To optimize the calculations, it is advisable to clip the DEM layer based on the shape of the vector layer that outlines the drainage basin.

![img_5a](https://github.com/user-attachments/assets/5b54ee8b-a67b-4ac5-95b8-ae29387ae621)

![img_5b](https://github.com/user-attachments/assets/be372937-d030-4e6b-a69a-9fda1f8585ac)
