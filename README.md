# 📈 Hypsometric Curve (QGIS 4 / Qt6)

## Hypsometric Curve is a QGIS 4 plugin for calculating and visualizing the hypsometric curve of a watershed using a Digital Elevation Model (DEM) and a boundary polygon.

### 🎯 Designed for scientific accuracy, speed, and modularity — ideal for geomorphology, hydrology, and geology.

## ✨ Features
### 📊 Hypsometric curve computation (h/H vs a/A)
### 📐 Calculates:
* h_min, h_max
* h_mean (mean basin elevation)
* HI – Hypsometric Integral
* Partial & cumulative areas

## ⚡ High performance rasterization via GDAL (ALL_TOUCHED=TRUE)
### 🧩 Modular and maintainable architecture
### 🖥️ Full compatibility with QGIS 4 + Qt6
### 🎨 Interactive graph:
* Custom color
* HI projection on curve
* Grid + optimized layout
### 💾 Export:
* CSV table
* PNG/JPG graph

## 🚀 Usage
### 📥 Load:
* DEM
* Watershed polygon
### 🔧 Open plugin:
* Plugins → Hypsometric Curve
* or toolbar
### ⚙️ Select:
*DEM
*Band
*Polygon
*Number of classes
### ▶️ Click Calculate
### 💾 Export:
* CSV table
* Graph (PNG/JPG)

## 🧠 Methodology
The hypsometric curve follows the classical definition:
* a/A → normalized cumulative area
* h/H → normalized cumulative elevation
### 📌 Hypsometric Integral (HI)
HI=(hmed−hm​in)/(hm​ax−hm​in)

### 🧮 Rasterization
gdal.RasterizeLayer(..., options=["ALL_TOUCHED=TRUE"])

## ✅ Validation
Tested with:
* 🌍 SRTM DEM (30 m)
* 🛰️ LiDAR DEM (1 m)
* 📏 Basins from 0.5–500 km²
* 🗺️ UTM & national CRS

## 👨‍🔬 Author
Dr. Geol. Faustino Cetraro
🧭 Scientific communicator & editorial architect

## 📜 License
Released under GNU GPL v2 or later

## 🤝 Contributions
Contributions are welcome!
* 🐛 Open an issue
* 🔧 Submit a pull request

# 📄 Changelog
[v1.1.0] – Major Refactor (QGIS 4 / Qt6)
📅 2026-03-28

## 🚀 New Features
* ✅ Full compatibility with QGIS 4 + Qt6
* 🧩 Modular architecture (GUI + core separation)

## 🖥️ UI/UX
* 🎨 Redesigned dialog (Qt Designer)
* 📐 Improved layout

## 🌍 Internationalization
* 🌐 .qm translation support
* ⚙️ Auto locale detection

## ⚠️ Breaking Changes
* ❗ Requires QGIS 4+
* 🚫 QGIS 3 / Qt5 no longer supported
* 🔥 Internal API changed

## 🔜 Roadmap
* 🗺️ CRS validation
* 🚫 Improved NoData handling
