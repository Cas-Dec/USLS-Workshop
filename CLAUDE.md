# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Purpose

3-day hands-on data science workshop for biology students at USLS, Bacolod, Philippines. Students have little to no programming experience. Notebooks run in **Google Colab**; no local installation is required for students.

## Environment Setup (local development)

```bash
conda env create -f environment.yml   # creates env named 'usls'
conda activate usls
pip install -e .                      # installs workshop_utils in editable mode
```

The package uses `pyprojroot` to locate the project root (by finding `pyproject.toml`), so `pip install -e .` must be run from the repo root.

## Repository Structure

- `notebooks/` — Student-facing notebooks (`intro.ipynb`, `day1.ipynb`, `day2.ipynb`, `day3.ipynb`).
  Load data via literal relative paths (e.g. `../data/processed/day1/best_yearly.csv`) rather than the
  `PROCESSED_DIR` constant — kept deliberately transparent for students with little programming
  background. Each notebook's Colab setup cell ends with `%cd notebooks`, so the working directory is
  the notebook's own folder in both Colab and local Jupyter, and a literal relative path resolves the
  same way in either environment.
- `behind-the-scenes/` — Instructor notebooks for data preparation (not shown to students). These use
  `RAW_DIR`/`PROCESSED_DIR` freely (instructor-only tooling) and call into `src/workshop_utils/download.py`
  for anything that fetches or prepares external data, rather than downloading inline.
- `src/workshop_utils/` — Helper package that abstracts complexity away from notebooks
- `data/raw/` — Raw data organized by source (`BEST/`, `NASA/`, `NOAA/`, `ERA5/`, `Beck/`, `GBIF/`,
  `Hansen/`, `Sentinel2/`, `WorldClim/`)
- `data/processed/` — Cleaned/preprocessed data consumed by student notebooks. Partitioned by day for
  day-specific outputs (`day1/`, `day2/`, `day3/` — e.g. GBIF species tables, Negros imagery, paleoclimate
  time series). Cross-cutting foundational reference layers that get reused across multiple days (KG
  classification, climate normals, land-sea masks at any resolution, WorldClim bioclim, DEM) stay at the
  top level rather than being duplicated into a day folder — see the "Data Sources" table below for which
  is which.
- `figures/` — Generated plots
- `download_tp.py` — Standalone script for bulk ERA5 precipitation download via Copernicus CDS API

## Architecture: `workshop_utils`

The package hides implementation complexity so notebooks stay pedagogically clean.

**`__init__.py`** — Sets path constants using `pyprojroot`:
- `PROJECT_ROOT`, `DATA_DIR`, `RAW_DIR`, `PROCESSED_DIR`
- Auto-creates `data/raw/` and `data/processed/` on import

**`config.py`** — Colab-aware output paths:
- Detects Google Colab by checking if `/content/drive` exists
- Sets `WORKSHOP_ROOT` to `MyDrive/biology-workshop` (Colab) or `./biology-workshop` (local)
- Provides `DATA_DIR`, `FIGURES_DIR`, `RESULTS_DIR` relative to `WORKSHOP_ROOT`

**`data_utils.py`** — Data loading:
- `launch_ARCO_ERA5()` — lazy singleton connection to ARCO-ERA5 public Zarr store on GCS (anonymous access)
- `download_var(var, timestamp)` — downloads a single ERA5 variable/timestamp to `data/raw/ERA5/<var>/`
- `load_lsm()` — loads land-sea mask, downloading on the fly if missing

**`download.py`** — Fetches and lightly parses external datasets. Scope is "get me a clean
DataFrame/Dataset back"; deciding where under `data/processed/` a result belongs (day-specific vs.
shared top-level) stays the caller's job — these functions never hardcode a day-folder, only ever
`RAW_DIR` for intermediate downloads. Behind-the-scenes notebooks should call into these rather than
re-implementing a fetch inline.
- `download_era5_copernicus()` — ERA5 reanalysis via the Copernicus CDS API; requires a configured `~/.cdsapirc` file
- Day 1 global/paleoclimate time series: `download_best()`, `download_gistemp()`, `download_mauna_loa_co2()`,
  `download_enso()`, `download_aod()`, `download_tsi()`, `download_epica()`, `download_vostok_co2()`
- `download_beck_climate_and_kg()` — Beck et al. Köppen-Geiger classification + 1 km/0.1° climate ensemble
  (figshare), pruned to the periods/resolutions the workshop needs and cropped to the Philippines bbox
- `download_gbif()` / `download_gbif_compilation()` — single-species and whole-taxon-compilation GBIF
  occurrence pulls
- `download_hansen_tiles()` — windowed remote reads of Hansen Global Forest Change COGs; only the
  bbox-sized window is transferred, never a full global tile
- `search_seasonal_scenes()` / `build_landsat_sentinel_composite()` — cloud/shadow-masked, season-matched
  Sentinel-2 + Landsat temporal-median compositing onto one shared lat/lon grid
- `download_worldclim_bioclim()` — crops a WorldClim 2.1 bioclim variable straight out of the remote
  9.7 GB zip via GDAL's `/vsizip/vsicurl/`, never downloading the full archive
- `build_dem_mosaic()` — aggregates Copernicus DEM GLO-30 onto an existing target grid via
  windowed/decimated remote reads; native ~30 m tiles are never written to disk

**`plotting.py`** — `save_figure(fig, name, figures_dir)` saves at 300 DPI

## Key Design Decisions

- Notebooks begin with a setup cell that clones the repo and installs the package in Colab
  (`!git clone ... && pip install -q .`), then ends with `%cd notebooks` so the working directory
  matches local Jupyter's default (the notebook's own folder) — this is what lets student notebooks use
  a literal relative path like `../data/processed/...` identically in both environments
- Path handling splits between two systems: `__init__.py` paths (repo-relative, for data I/O in
  `workshop_utils`/behind-the-scenes tooling) and `config.py` paths (Drive-relative, for student outputs)
- The ARCO-ERA5 connection (`_ARCO_DS`) is a module-level singleton to avoid repeated network connections
- ERA5 code commented out in `data_utils.py` (Google Earth Engine functions) is intentionally left as reference

## Data Sources

| Dataset | Source | Location |
|---|---|---|
| Berkeley Earth global temp | Berkeley Earth | `data/processed/day1/best_yearly.csv` |
| NASA GISTEMP | NASA GISS | `data/processed/day1/gistemp_yearly.csv` |
| Mauna Loa CO₂, ENSO, TSI, AOD | NOAA / NASA GISS | `data/processed/day1/` |
| EPICA Dome C, Vostok ice cores | NOAA paleoclimatology | `data/processed/day1/` |
| ERA5 reanalysis | Copernicus / ARCO-ERA5 | `data/raw/ERA5/`; Bacolod monthly climatology shared at `data/processed/t2m_bacolod_monthly.nc` / `tp_bacolod_monthly.nc` (Day 1 + Day 2) |
| Köppen-Geiger classification + climate ensemble | Beck et al. (2023), figshare | `data/processed/kg_philippines_*.nc`, `climate_philippines_*.nc` — shared across Day 1/2/3 |
| Land-sea masks (0.25°/0.1°/1 km) | ERA5 / derived from Beck ensemble | `data/processed/land_sea_mask*.nc`, `land-sea-mask_0p00833333.nc` — shared |
| WorldClim 2.1 bioclim (BIO5, BIO14) | WorldClim, 30 arc-sec, 1970–2000 baseline | `data/processed/worldclim_bio_philippines_1970_2000.nc` — shared (Day 3 SDM) |
| Copernicus DEM GLO-30 | ESA/Copernicus via Microsoft Planetary Computer | `data/processed/dem_philippines_1km.nc` — shared (Day 3 SDM) |
| GBIF species occurrences + mammal compilation | GBIF | `data/processed/day2/gbif_*.csv` |
| Sentinel-2 / Landsat imagery, Hansen forest change | Element84 / Planetary Computer / Hansen et al. | `data/processed/day2/negros_*.nc` |
