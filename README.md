# Spatial Interpolation Project

This project provides a Python script (`main.py`) for performing various spatial interpolation techniques on geospatial grid data, typically derived from shapefiles. It supports **Thiessen**, **Bilinear**, and **Inverse Distance Weighting (IDW)** interpolation, allowing for the processing of both complete and incomplete grids. The interpolated results are visualized and saved as PNG images.

---

## 🧰 Features

- **Shapefile to Grid Conversion**: Reads point data from ESRI Shapefiles (`.shp`) and converts them into a 2D NumPy array grid.
- **Thiessen Interpolation**: Uses nearest neighbor interpolation for upscaling complete grids.
- **Bilinear Interpolation**: Smooths grid upscaling using values from four nearest input points.
- **Inverse Distance Weighting (IDW)**: Fills missing values in incomplete grids using a weighted average based on distance.
- **Visualization**: Saves color-mapped visualizations of interpolated grids using `matplotlib`.
- **Output Management**: Automatically organizes output images by interpolation method.

---

## 🚀 Getting Started

### Prerequisites

Install required Python packages:

```bash
pip install numpy matplotlib scipy geopandas
```

---

## 📁 Project Structure

```
.
├── main.py
├── DatotekePolnaMreza/
│   ├── grid_full_1.shp
│   └── grid_full_2.shp
├── DatotekeManjkajoceTocke/
│   ├── grid_missing_1.shp
│   └── grid_missing_2.shp
└── output/
    ├── thiessen/
    ├── bilinear/
    └── idw/
```

- `main.py`: Main script with interpolation logic.
- `DatotekePolnaMreza/`: Shapefiles for **complete** grids (Thiessen, Bilinear).
- `DatotekeManjkajoceTocke/`: Shapefiles for **incomplete** grids (IDW).
- `output/`: Auto-created; stores results in method-specific folders.

---

## ⚙️ Setup and Running

### 1. Prepare Your Data

- Create two folders:
  - `DatotekePolnaMreza` for full (complete) grid shapefiles.
  - `DatotekeManjkajoceTocke` for grids with missing data.

- Place your `.shp` files (with accompanying `.dbf`, `.shx`, etc.) in the appropriate folders.

- Make sure the shapefiles include a numeric field named `'Z'` (or modify the `z_field` in the code accordingly).

### 2. Run the Script

```bash
python main.py
```

The script processes all shapefiles, applies interpolation methods, and saves results in the `output/` directory. Status updates will be printed to the console.

---

## 📈 Interpolation Methods Explained

### 🟦 Thiessen Interpolation (`thiessen_interpolation`)
- Assigns each output cell the value of the closest known point.
- Fast and simple.
- Results in a blocky, discrete appearance.
- Used for **upscaling** full grids.

### 🟨 Bilinear Interpolation (`bilinear_interpolation`)
- Uses four nearest points to compute a weighted average.
- Produces smoother output.
- Also used for **upscaling** full grids.

### 🟥 Inverse Distance Weighting - IDW (`idw_interpolation`)
- Estimates unknown values based on surrounding known points.
- Weights are inversely proportional to distance (default exponent = 2).
- Effective for **filling missing values** in incomplete datasets.

---

## 🛠️ Configuration

You can customize key parameters in the `main()` function in `main.py`:

```python
def main():
    factor = 7              # Upscaling factor for Thiessen/Bilinear
    k_neighbors = 4         # Number of neighbors for IDW
    power = 2               # IDW weighting power
    full_dir = 'DatotekePolnaMreza'
    missing_dir = 'DatotekeManjkajoceTocke'
    out_dir = 'output'
```

---

## 📤 Output

Results are saved in:

```
output/
├── thiessen/
├── bilinear/
└── idw/
```

Each subfolder contains PNG images named after the original shapefile (e.g., `grid_full_1.png`).

---

## ⚠️ Limitations

- **Input Format**: Only supports ESRI Shapefiles with point geometries and a `'Z'` field.
- **Coordinate Systems**: Assumes consistent CRS across all files (no reprojection applied).
- **Interpolation Scope**: Uses basic methods; not suitable for advanced geostatistics (e.g., kriging).
- **Performance**: Pure Python implementation may be slow for very large datasets.
