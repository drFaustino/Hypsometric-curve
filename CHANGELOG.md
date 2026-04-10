# 📄 Changelog – Hypsometric Curve (QGIS Plugin)
All notable changes to this project will be documented in this file.

## [v1.1.2] – 2026-04-10
UI/UX Fixes, Color System Rewrite & Validation Improvements

### 🎨 Color System Overhaul
* Replaced pushButton_color + lbl_color with native QgsColorButton.
* Removed all obsolete color-handling code:
 - selected_color
 - ColorDialog
 - stylesheet parsing
 - label synchronization
 - Graph now always uses the color from QgsColorButton.
 - Fixed issue where the graph did not update on first run.
 - Added support for default color initialization (UI or Python).

### 📊 Graph Rendering Fixes
* Fixed crash caused by self.selected_color being None.
* Graph now updates correctly after:
 - color change
 - reset
 - recalculation
 - Fixed progress bar freezing at 40% due to graph exceptions.

### 🧩 Reset & Output Fields
Reset now correctly resets:
 - h_min, h_max, h_med, HI
 - A (area) field (previously not cleared)
 - Added option to reset fields to 0 instead of empty.

### ⚠️ Validation & User Feedback
Added warnings for:
 - Calculate → if DEM, band, or polygon are missing.
 - Save Table → if table is empty.
 - Save Graph → if graph/table not computed yet.
 - Messages are now clearer and prevent invalid operations.

### 🔧 Internal Cleanup
* Removed unused imports and dead code.
* Simplified GraphManager logic.
* Improved consistency between UI and backend.

## [v1.1.1] – 2026-04-10
### Stability & QGIS 4 Fixes
### 🛠️ Geometry & CRS Fixes
 - Fixed critical error: AttributeError: 'GeometryOperationResult' object has no attribute 'asWkt'.
 - Added robust handling of GeometryOperationResult across all geometry operations.
 - Corrected CRS transformation logic:
 - geom.transform() (in-place) now handled properly.
 - Automatic unwrapping of geometry results.
 - Full compatibility with QGIS 4 geometry API.
 - Fixed rasterization failures when DEM is in geographic coordinates (EPSG:4326).

### 🎨 Graph & UI Fixes
 - Fixed issue where the initial curve color was always gray.
 - The initial graph color is now correctly synchronized with the lbl_color background.
 - Implemented stylesheet-based color extraction (Qt palette does not reflect stylesheet colors).
 - Ensured Matplotlib uses the selected color via ax.set_prop_cycle().

### 🧠 Scientific Corrections
Corrected Hypsometric Integral (HI) computation:
 - Now uses real mean elevation (h_med) instead of interval midpoints.
 - Fixed issue where HI was always 0.50.
 - Results now match classical geomorphological definitions (Pike & Wilson, 1971).

### 🔧 Internal Improvements
 - Improved raster masking robustness.
 - Safer NoData handling.
 - Cleaner module structure and naming consistency.
 - Improved graph initialization and color management.

## [v1.1.0] – 2026-03-28
### Major Refactor (QGIS 4 / Qt6)
(contenuto invariato)

### 🔜 Planned (Future Versions)
 - CRS validation with projected CRS warnings.
 - Improved NoData handling.
 - Multi-basin support.
 - Batch processing.
 - CSV/GeoPackage export.
 - Interactive zoom/pan on graph.
 - Dockable panel version.