# Hypsometric curve
## QGIS plugin
### version 0.1, minimum required QGIS v. 3.x

Calculates the **hypsometric curve** of a drainage basin from a terrain DEM layer and the definition of the perimeter of the basin, obtained from a vector layer containing the polygon that delimits its boundaries. It is possible to choose the number of bands for the terrain elevations and define the number of classes of the elevation intervals to divide the area of ​​the basin itself. As a result, the minimum, maximum and average elevation inside the basin polygon, the total area and the value of the hypsometric integral are calculated. In addition, the graph of the hypsometric curve is drawn, with the relative calculated values ​​reported in a table. It is possible to save both the graph in image format and the table of values ​​in a CSV or TXT file.

The plugin requires the use of the **numpy**, **matplotlib**, **pyplot** and **csv** libraries.

## Plugin interface
The plugin interface is simple and intuitive, designed to facilitate the analysis of the river basin. It is organized into three main menus:

**Selection of the raster layer (DEM)**: allows you to choose the raster layer containing the Digital Elevation Model (DEM).

**Choice of the band**: allows you to specify the number of the band to use in the calculation.

**Selection of the vector layer**: is used to indicate the vector layer that contains the polygon delimiting the river basin.

In addition to the main menus, the interface includes a control dedicated to defining the number of elevation intervals to be considered within the boundaries of the basin.

> **Results**

The processing returns the following results:

- Minimum, maximum and average elevation within the polygon delimiting the basin.
- Total area of ​​the basin.
- Value of the hypsometric integral.

**Additional features**

The plugin automatically generates the hypsometric curve graph, whose calculated values ​​are also reported in a searchable table. You can export the results thanks to two saving options:

- The graph can be saved as an image in various formats.
- The table of values ​​can be exported to a CSV or TXT file for further analysis.

The interface is designed to ensure a simple and effective workflow, combining data visualization and analysis in a practical way.

![img_2](https://github.com/user-attachments/assets/d801172e-eb46-4b0f-84f4-83e2f16cffb8)

> **Important Notes**

To perform the calculations accurately, it is essential to use a **projected reference system** (for example, the UTM system). This ensures that the measurements, both of the elevations of the terrain and of the areas, are correct and consistent.

Furthermore, it is essential that **both layers** involved in the analysis, namely the *DEM raster layer* and the *vector layer* containing the basin polygon, **are in the same projected reference system**.

## Update - version 0.2

In this version, several new features have been implemented to improve the interactivity and usability of the application. Among the main new features:

- **Assigning color to the hypsometric curve**: You can customize the color of the curve using the Color button. This allows you to change the graphic appearance of the graph in a simple and immediate way.
- **Updating the graph without recalculation**: After assigning a color to the curve, the graph is dynamically updated without the need to recalculate the data. This feature ensures greater efficiency and a better user experience.
- **Displaying useful information**: Features have been added to display significant details such as the HI (Hypsometric Index) index and other related data, directly on the graph, offering a clearer and more complete representation.

Thanks to these new features, the application is more versatile and intuitive, better responding to user needs.

![fig_3](https://github.com/user-attachments/assets/b4ce74eb-aaa0-4aee-9c9e-4fb5af563797)

New interface with the addition of more information and the ability to change the color of the curve

![fig_4](https://github.com/user-attachments/assets/1b6d72cc-6de7-4b2b-a459-17460ec23791)

The Table tab shows the calculated values ​​with the possibility of saving them to a file

![fig_5](https://github.com/user-attachments/assets/c0d7ebfd-cd2a-48b1-bc3b-4f919945719b)


## Update - version 0.3

In this release several bugs have been fixed, the user interface has been optimized, the new "**Refresh**" command has been introduced to update the graph display, additional checks and warnings have been implemented to improve the user experience.

![img_1a](https://github.com/user-attachments/assets/f9983ec3-b07a-4e4d-8d4f-fdccc120255e)

## Update - version 0.4

Added files to display the interface in Italian and English languages.

## Update - version 0.5

In the improved version, a new calculation mode for hmed and HI has been introduced. Additional controls have been added on the raster layer and new fields have been implemented in the table to display additional information. Float32 and Float64 data are now supported. Additionally, the interface has been remodeled to accommodate the new elements inserted. To optimize the calculations, it is advisable to clip the DEM layer based on the shape of the vector layer that outlines the drainage basin.

![img_5a](https://github.com/user-attachments/assets/5b54ee8b-a67b-4ac5-95b8-ae29387ae621)

![img_5b](https://github.com/user-attachments/assets/be372937-d030-4e6b-a69a-9fda1f8585ac)
