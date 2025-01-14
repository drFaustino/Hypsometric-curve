# Hypsometric curve
## QGIS plugin
### version 0.6, minimum required QGIS v. 3.x

Calculates the **hypsometric curve** of a drainage basin from a terrain DEM layer and the definition of the perimeter of the basin, obtained from a vector layer containing the polygon that delimits its boundaries. It is possible to choose the number of bands for the terrain elevations and define the number of classes of the elevation intervals to divide the area of ​​the basin itself. As a result, the minimum, maximum and average elevation inside the basin polygon, the total area and the value of the hypsometric integral are calculated. In addition, the graph of the hypsometric curve is drawn, with the relative calculated values ​​reported in a table. It is possible to save both the graph in image format and the table of values ​​in a CSV or TXT file.

The plugin requires the use of the **numpy**, **matplotlib**, **pyplot** and **csv** libraries.

In this version some bugs have been fixed, new controls have been added and the translation for the **Spanish** language has been added.
The current version is translated into **Italian**, **English** and **Spanish**.

![Primo](https://github.com/user-attachments/assets/691ddfc5-6cd0-4572-a282-2c9ad2316dd9)

![Secondo](https://github.com/user-attachments/assets/cb761de0-64a1-4be8-aa1f-82e84ffcbdd5)
