#!/usr/bin/env python3
"""Convert local PMTiles in output/ to CSV.

This script expects PMTiles in the local output/ folder and writes CSVs to the
same folder.

How to use:
1. After clone this repository and update pmtiles files in the output/ folder,
   run this script to convert all PMTiles to CSV files.
   
   python pmtiles_to_csv.py
   
2. You should see .csv files created in the output/ folder. Push your changes back to GitHub.

Notes:
- Requires `geopandas` and a GDAL build with PMTiles support.
- Large PMTiles can be memory-heavy; this loads each file into memory.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import geopandas as gpd


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Convert local PMTiles to CSV.")
    parser.add_argument(
        "--output-dir",
        default="output",
        help="Local folder containing .pmtiles (default: output).",
    )
    parser.add_argument(
        "--to-crs",
        default=None,
        help="Optional target CRS (e.g. EPSG:4326) applied before export.",
    )
    return parser.parse_args()


OUTPUT_COLUMNS = ["category", "name", "address", "city", "state", "zip", "confidence"]


def convert_pmtiles_to_csv(
    pmtiles_path: Path, csv_path: Path, to_crs: str | None
) -> None:
    gdf = gpd.read_file(pmtiles_path)
    if to_crs:
        gdf = gdf.to_crs(to_crs)
    df = gdf.drop(columns=["geometry"], errors="ignore").copy()
    for col in OUTPUT_COLUMNS:
        if col not in df.columns:
            df[col] = ""
    df = df[OUTPUT_COLUMNS]
    df.to_csv(csv_path, index=False)


def main() -> None:
    args = parse_args()
    out_dir = Path(args.output_dir).resolve()
    pmtiles_files = sorted(out_dir.glob("*.pmtiles"))
    if not pmtiles_files:
        print(f"No .pmtiles files found in {out_dir}.")
        return
    for pm_local in pmtiles_files:
        csv_local = out_dir / (pm_local.stem + ".csv")
        print(f"Converting {pm_local.name} -> {csv_local.name}...")
        convert_pmtiles_to_csv(pm_local, csv_local, args.to_crs)


if __name__ == "__main__":
    main()
