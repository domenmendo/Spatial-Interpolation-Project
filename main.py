#!/usr/bin/env python3
import os
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import KDTree
import geopandas as gpd

def shapefile_to_grid(shp_path, z_field='Z'):
    gdf = gpd.read_file(shp_path)
    xs = np.sort(gdf.geometry.x.unique())
    ys = np.sort(gdf.geometry.y.unique())
    nx, ny = len(xs), len(ys)
    Z = np.full((ny, nx), np.nan)
    x_to_j = {x: j for j, x in enumerate(xs)}# map x-coordinates to column indices
    y_to_i = {y: i for i, y in enumerate(ys)}# map y-coordinates to row indices
    for _, row in gdf.iterrows():
        x, y = row.geometry.x, row.geometry.y
        i, j = y_to_i[y], x_to_j[x]
        Z[i, j] = row[z_field]
    return Z, xs, ys # Z: 2D array of values, xs: x-coordinates, ys: y-coordinates 

def thiessen_interpolation(Z_in, factor): # every point in output grid is assigned the value of the nearest point in input grid
    M, N = Z_in.shape #M=row, N=col
    M_out, N_out = int(M * factor), int(N * factor)
    Z_out = np.empty((M_out, N_out))
    for i_out in range(M_out):
        for j_out in range(N_out):
            x = i_out / factor # calc position in input grid
            y = j_out / factor
            i_nn = int(round(x)); j_nn = int(round(y))# round to nearest neighbor
            i_nn = min(max(i_nn, 0), M-1) # edge case: ensure within bounds
            j_nn = min(max(j_nn, 0), N-1)
            Z_out[i_out, j_out] = Z_in[i_nn, j_nn]
    return Z_out

def bilinear_interpolation(Z_in, factor):
    M, N = Z_in.shape #M=row, N=col
    M_out, N_out = int(M * factor), int(N * factor)
    Z_out = np.empty((M_out, N_out))
    for i_out in range(M_out):
        for j_out in range(N_out):
            x = i_out / factor # calc position in input grid
            y = j_out / factor
            i0, j0 = int(np.floor(x)), int(np.floor(y)) # bottom left corner
            i1, j1 = min(i0+1, M-1), min(j0+1, N-1) # -1 to avoid index out of bounds
            α, β = x - i0, y - j0 # example: x=3.4 i0=3, i1=4, α=0.4
            s00 = Z_in[i0, j0]; s10 = Z_in[i1, j0]
            s01 = Z_in[i0, j1]; s11 = Z_in[i1, j1]
            Z_out[i_out, j_out] = (
                (1-α)*(1-β)*s00 +
                α*(1-β)*s10 +
                (1-α)*β*s01 +
                α*β*s11
            )
    return Z_out

def idw_interpolation(Z_in, k=4, power=2): # closer point gets more weight
    M, N = Z_in.shape
    known = [(i, j) for i in range(M) for j in range(N) if not np.isnan(Z_in[i, j])] # list of indexes with known values
    values = [Z_in[i, j] for i, j in known]
    tree = KDTree(known)
    Z_out = Z_in.copy() # fixing NaNs in output grid
    for i in range(M):
        for j in range(N):
            if np.isnan(Z_out[i, j]):
                dists, idxs = tree.query((i, j), k=min(k, len(known))) # find k nearest neighbors
                dists = np.maximum(dists, 1e-12) # if 0 set to 1e-12
                w = 1.0 / (dists**power) # inverse distance weighting
                Z_out[i, j] = np.dot(w, [values[idx] for idx in idxs]) / w.sum() # np.dot(w, values_list) / w.sum()
    return Z_out

def plot_and_save(Z, title, out_path): # visualize 2d colored array and save to file
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.figure(figsize=(6,5))
    plt.imshow(Z, origin='lower', cmap='viridis')
    plt.colorbar(label='Višina')
    plt.title(title)
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()

# Main processing functions for full and incomplete grids
def process_full_grid(shp_dir, factor, out_dir):
    for fname in os.listdir(shp_dir):
        if not fname.endswith('.shp'): continue
        base = os.path.splitext(fname)[0]
        shp_path = os.path.join(shp_dir, fname)
        Z, xs, ys = shapefile_to_grid(shp_path)
        # Thiessen
        Z_th = thiessen_interpolation(Z, factor)
        plot_and_save(Z_th, f'{base}: Thiessen', os.path.join(out_dir, 'thiessen', f'{base}_thiessen.png'))
        # Bilinear
        Z_bl = bilinear_interpolation(Z, factor)
        plot_and_save(Z_bl, f'{base}: Bilinear', os.path.join(out_dir, 'bilinear', f'{base}_bilinear.png'))
        print(f"[OK] {base}: Thiessen & Bilinear")

# Process incomplete grids with IDW interpolation
def process_incomplete_grid(shp_dir, k, power, out_dir):
    for fname in os.listdir(shp_dir):
        if not fname.endswith('.shp'): continue
        base = os.path.splitext(fname)[0]
        shp_path = os.path.join(shp_dir, fname)
        Z, xs, ys = shapefile_to_grid(shp_path)
        Z_idw = idw_interpolation(Z, k=k, power=power)
        plot_and_save(Z_idw, f'{base}: IDW', os.path.join(out_dir, 'idw', f'{base}_idw.png'))
        print(f"[OK] {base}: IDW")

def main():
    # Parametri
    factor = 7            # faktor povečave za Thiessen/Bilinear
    k_neighbors = 4       # število sosedov za IDW
    power = 2             # potenca za IDW
    full_dir = 'DatotekePolnaMreza'
    missing_dir = 'DatotekeManjkajoceTocke'
    out_dir = 'output'

    process_full_grid(full_dir, factor, out_dir)
    process_incomplete_grid(missing_dir, k_neighbors, power, out_dir)
    print("Vse interpolacije so končane in shranjene v 'output/'.")

if __name__ == '__main__':
    main()
