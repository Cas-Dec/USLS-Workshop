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

- `notebooks/` — Student-facing notebooks (`intro.ipynb`, `day1.ipynb`, `day2.ipynb`, `day3.ipynb`)
- `behind-the-scenes/` — Instructor notebooks for data preparation (not shown to students)
- `src/workshop_utils/` — Helper package that abstracts complexity away from notebooks
- `data/raw/` — Raw data organized by source (`BEST/`, `NASA/`, `NOAA/`, `ERA5/`)
- `data/processed/` — Cleaned/preprocessed data consumed by student notebooks
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

**`download.py`** — CDS API wrapper:
- `download_era5_copernicus()` — downloads ERA5 from Copernicus Climate Data Store; requires a configured `~/.cdsapirc` file

**`plotting.py`** — `save_figure(fig, name, figures_dir)` saves at 300 DPI

## Key Design Decisions

- Notebooks begin with a setup cell that clones the repo and installs the package in Colab (`!git clone ... && pip install -q .`)
- Path handling splits between two systems: `__init__.py` paths (repo-relative, for data I/O) and `config.py` paths (Drive-relative, for student outputs)
- The ARCO-ERA5 connection (`_ARCO_DS`) is a module-level singleton to avoid repeated network connections
- ERA5 code commented out in `data_utils.py` (Google Earth Engine functions) is intentionally left as reference

## Data Sources

| Dataset | Source | Location |
|---|---|---|
| Berkeley Earth global temp | Berkeley Earth | `data/raw/BEST/` |
| NASA GISTEMP | NASA GISS | `data/raw/NASA/` |
| Mauna Loa CO₂, ENSO, TSI | NOAA | `data/raw/NOAA/` |
| ERA5 reanalysis | Copernicus / ARCO-ERA5 | `data/raw/ERA5/` |
