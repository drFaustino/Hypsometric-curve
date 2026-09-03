# Hypsometric Curve – QGIS Plugin
A modern, modular, QGIS 4–compatible tool for computing and visualizing hypsometric curves.

Note: interface in Italian and English.

<img width="1007" height="803" alt="img2" src="https://github.com/user-attachments/assets/b713eda6-7784-48f3-baba-3ee67cd00b24" />


### 🌄 Overview
* Hypsometric Curve is a scientific plugin for QGIS designed to compute:
* Elevation intervals
* Partial and cumulative areas
* Mean elevation (h_med)
* Hypsometric Integral (HI)
* Normalized hypsometric curves (a/A vs h/H)

It provides a clean, interactive interface and a fully modular backend optimized for QGIS 4 and Qt6.

### ✨ Key Features
🔬 Scientific Computation
- Accurate hypsometric curve generation.
- Correct HI computation (Pike & Wilson, 1971).
- Support for high-resolution class intervals (10–500).
- Robust NoData and mask handling.

### 🗺️ Raster & Vector Processing
- Automatic detection of:
- DEM raster layers
- Raster bands
- Polygon layers (basins/watersheds)
- GDAL-based rasterization with ALL_TOUCHED=TRUE.
- CRS transformation fully compatible with QGIS 4.

### 📊 Graph & Table Output
- Interactive graph rendered inside a QGraphicsView.
- Customizable curve color via QgsColorButton.
- Optional HI projection on the curve.
- Export graph as PNG/JPG.
- Export table values.

### 🖥️ User Interface
Clean, organized layout:
- Input parameters
- Results
- Graph
- Table
- Reset and refresh buttons.
- Progress bar for long operations.
- Automatic locale detection and translation support.
- Validation warnings for missing layers or empty tables.

### ⚠️ Important Notes
Always use a projected CRS for correct area and elevation calculations.
The Hypsometric Integral (HI) ranges from:
- 0 → highly eroded landscapes
- 1 → slightly eroded landscapes

Geographic CRS (e.g., EPSG:4326) may cause incorrect area values.

### 🛠️ Requirements
- QGIS 4.0+
- Python 3.12+
- Qt6
- GDAL (included with QGIS)
- Older versions of QGIS (3.x) are not supported.

### 📥 Installation
- Download the plugin folder or ZIP.
- Place it in your QGIS profile directory:
- Codice
<User>/AppData/Roaming/QGIS/QGIS4/profiles/<ProfileName>/python/plugins/
- Restart QGIS.

Enable the plugin from:
Plugins → Manage and Install Plugins

### 🚀 Usage
- Select a DEM raster.
- Select the raster band.
- Select a polygon layer representing the basin.
- Choose the number of elevation classes.
- Click Calculate.

View:
- h_min, h_max, h_med
- HI
- Hypsometric curve
- Table of intervals and areas

You can also:
- Change the curve color
- Refresh the graph
- Save the graph
- Export the table

Validation warnings will appear if:
- No DEM or polygon is selected
- The table is empty when saving
- The graph is not available

### 🧪 Scientific Reference
Pike, R.J. & Wilson, S.E. (1971).
Elevation–relief ratio, hypsometric integral, and geomorphic area–altitude analysis.  
Geological Society of America Bulletin.

### 📝 License
This plugin is released under the GPL v3 license.

### 👤 Author
Faustino Cetraro  
Geologist, scientific communicator, and QGIS plugin developer.

### 🤝 Contributions
Contributions, bug reports, and feature requests are welcome.
Please open an issue or submit a pull request on the repository.
