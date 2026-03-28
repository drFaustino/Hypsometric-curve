📄 Changelog – Hypsometric Curve (QGIS Plugin)
[v1.1.0] – Major Refactor (QGIS 4 / Qt6)

Release date: 2026/03/28

🚀 New Features
Full compatibility with QGIS 4 and Qt6
Modular architecture with separation between GUI and scientific logic
Added dedicated core modules:
RasterProcessor → raster preprocessing and masking
HypsometricCalculator → numerical computations
GraphManager → hypsometric curve plotting and export
TableManager → table population and export
Automatic detection of:
Raster layers (DEM)
Raster bands
Polygon layers (watershed boundaries)
Interactive graph visualization using QGraphicsView
Export functionalities:
Save hypsometric table
Save graph as image
Custom graph color selection
Progress bar for long operations

⚡ Improvements
Complete refactoring of calculation pipeline for better readability and maintainability
Optimized raster processing workflow (mask + cell area handling)
Improved UI responsiveness and interaction
Cleaner signal-slot connections for buttons
Better separation of responsibilities (MVC-like structure)
Dynamic UI update after each calculation
Graph refresh without recomputing data

🧠 Scientific Enhancements
Accurate computation of:
Elevation intervals
Partial and cumulative areas
Mean elevation (hmed)
Hypsometric Integral (HI)
Support for high-resolution class intervals (10–500)
Improved numerical stability of HI calculation

🖥️ UI/UX Changes
Redesigned dialog structure (Qt Designer)
Improved layout organization (ready for responsive layouts)
Clear separation between:
Input parameters
Results
Graph
Table
Added:
Reset functionality
Refresh graph button
Better feedback via progress bar

🌍 Internationalization
Added translation support via .qm files
Automatic locale detection from QGIS settings

🐞 Bug Fixes
Fixed issues with:
Missing layer selection validation
Incorrect band indexing
Graph not refreshing properly
Improved error handling with user-friendly messages

🔧 Internal Changes
Plugin entry point simplified and cleaned
Reduced code duplication
Improved naming consistency
Better integration with QGIS API (QgsProject, QgsRasterLayer, QgsVectorLayer)

⚠️ Breaking Changes
Requires QGIS 4+
Old versions (QGIS 3 / Qt5) are no longer supported
Internal API completely changed (custom scripts may break)

🔜 Planned (Future Versions)
CRS validation (projected CRS warning)
NoData handling improvements
Multi-basin support
Batch processing
Export to CSV/GeoPackage
Interactive zoom/pan on graph
Dockable panel version