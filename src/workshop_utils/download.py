# download.py - functions to download and lightly prepare data from the web
#
# Scope: fetching external datasets and doing the minimal parsing needed to get a clean,
# in-memory DataFrame/Dataset back. Deciding *where* under data/processed/ a result belongs
# (day1/day2/day3 vs. shared top-level) stays the caller's job -- these functions never
# hardcode a PROCESSED_DIR subfolder, only ever RAW_DIR for intermediate downloads.

# imports
import os
import shutil
import stat
import zipfile
from pathlib import Path

import cdsapi
import numpy as np
import pandas as pd
import requests
import xarray as xr
import rasterio
import rioxarray
import pystac_client
import planetary_computer
from rasterio.enums import Resampling
from rasterio.io import MemoryFile
from rasterio.merge import merge as rio_merge
from rasterio.warp import reproject
from rasterio.windows import from_bounds
from pyproj import Transformer

from workshop_utils import RAW_DIR, PROCESSED_DIR
from workshop_utils.data_utils import dir_exists


#================================
# ERA5 (Copernicus Climate Data Store)
#================================


def download_era5_copernicus(dataset: str = "reanalysis-era5-single-levels",
                             variable: list = ["2m_temperature"],
                             year: list = ["2025"],
                             month: list = ["01"],
                             day: list = ["01"],
                             time: list = ["00:00"],
                             daily_statistic: str = "daily_sum",
                             time_zone: str = "utc+00:00",
                             frequency: str = "1_hourly",
                             area: list = [90, -180, -90, 180],
                             output_path: str = None):

    request = {
        "product_type": ["reanalysis"],
        "variable": variable,
        "year": year,
        "month": month,
        "day": day,
        "data_format": "netcdf",
        "area": area
    }

    if dataset == "reanalysis-era5-single-levels":
        request.update({
            "time": time,
            "download_format": "unarchived"
        })
    elif dataset == "derived-era5-single-levels-daily-statistics":
        request.update({
            "daily_statistic": daily_statistic,
            "time_zone": time_zone,
            "frequency": frequency
        })

    if output_path is None:
        output_path = RAW_DIR / "ERA5" / f"{variable[0]}" / f"{variable[0]}.nc"

    dir_exists(output_path)

    client = cdsapi.Client()
    client.retrieve(dataset, request).download(output_path)


#================================
# Day 1 -- global / paleoclimate time series
#================================


def download_best(nrows: int = 2100) -> pd.DataFrame:
    """Berkeley Earth (BEST) global land+ocean temperature anomaly -> yearly mean."""
    url = "https://berkeley-earth-temperature.s3.us-west-1.amazonaws.com/Global/Land_and_Ocean_complete.txt"
    raw_path = RAW_DIR / "BEST" / "berkeley_earth_global_temp.txt"
    if not raw_path.exists():
        dir_exists(raw_path)
        raw_path.write_text(requests.get(url).text)

    columns = [
        "Year", "Month", "Anomaly_Monthly", "Unc_Monthly",
        "Anomaly_Annual", "Unc_Annual", "Anomaly_FiveYear", "Unc_FiveYear",
        "Anomaly_TenYear", "Unc_TenYear", "Anomaly_TwentyYear", "Unc_TwentyYear",
    ]
    df = pd.read_csv(raw_path, comment="%", sep=r"\s+", header=None, names=columns, nrows=nrows)
    best_yearly = df.groupby("Year")["Anomaly_Monthly"].mean().reset_index()
    best_yearly.columns = ["Year", "Anomaly"]
    return best_yearly


def download_gistemp() -> pd.DataFrame:
    """NASA GISTEMP global surface temperature anomaly -> yearly mean."""
    url = "https://data.giss.nasa.gov/gistemp/tabledata_v4/GLB.Ts+dSST.csv"
    raw_path = RAW_DIR / "NASA" / "gistemp_global.csv"
    if not raw_path.exists():
        dir_exists(raw_path)
        raw_path.write_text(requests.get(url).text)

    gistemp = pd.read_csv(raw_path, skiprows=1)
    month_cols = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    gistemp_long = gistemp.melt(id_vars=["Year"], value_vars=month_cols, var_name="month", value_name="Anomaly")
    gistemp_long["Anomaly"] = pd.to_numeric(gistemp_long["Anomaly"], errors="coerce")
    return gistemp_long.groupby("Year")["Anomaly"].mean().reset_index()


def download_mauna_loa_co2() -> tuple[pd.DataFrame, pd.DataFrame]:
    """NOAA Mauna Loa CO2 record -> (monthly, yearly) DataFrames."""
    url = "https://gml.noaa.gov/webdata/ccgg/trends/co2/co2_mm_mlo.csv"
    raw_path = RAW_DIR / "NOAA" / "mauna_loa_co2.csv"
    if not raw_path.exists():
        dir_exists(raw_path)
        raw_path.write_text(requests.get(url).text)

    co2_raw = pd.read_csv(raw_path, comment="#")
    co2_monthly = co2_raw[co2_raw["average"] > 0].copy()
    co2_yearly = co2_monthly.groupby("year")["average"].mean().reset_index()
    return co2_monthly, co2_yearly


def download_enso() -> pd.DataFrame:
    """ENSO (Nino3.4 index) via KNMI Climate Explorer -> yearly mean."""
    raw_path = RAW_DIR / "NOAA" / "nino.nc"
    if not raw_path.exists():
        url = "https://climexp.knmi.nl/data/iersst_nino3.4a_rel.nc"
        ds = xr.open_dataset(url, engine="h5netcdf", decode_times=False)
        dir_exists(raw_path)
        ds.to_netcdf(raw_path)

    nino_ds = xr.open_dataset(raw_path, decode_times=False)
    nino_ds["time"] = (
        pd.date_range(start="1854-01-01", periods=nino_ds.sizes["time"], freq="MS")
        + pd.Timedelta(days=14)
    )
    nino = nino_ds["Nino3.4r"]
    return (
        pd.DataFrame({"date": nino_ds["time"].values, "enso": nino.values})
        .assign(Year=lambda df: pd.DatetimeIndex(df["date"]).year)
        .groupby("Year")["enso"].mean()
        .reset_index()
    )


def download_aod() -> pd.DataFrame:
    """Stratospheric aerosol optical depth (AOD, volcanic activity proxy) -- NASA GISS."""
    url = "https://data.giss.nasa.gov/modelforce/strataer/data/tau_reff_Sato-Lacis.nc"
    raw_path = RAW_DIR / "NASA" / "sato_lacis_aod.nc"
    if not raw_path.exists():
        dir_exists(raw_path)
        raw_path.write_bytes(requests.get(url).content)

    aod_ds = xr.open_dataset(raw_path)
    aod_global = aod_ds["tau_lvl"].sum("level").mean("lat")
    time_dates = pd.to_datetime(aod_ds["month"].values)
    aod_years = time_dates.year + (time_dates.month - 1) / 12
    return pd.DataFrame({"year": aod_years, "aod": aod_global.values})


def download_tsi() -> tuple[pd.DataFrame, pd.DataFrame]:
    """NOAA Total Solar Irradiance (TSI), monthly files 1874-present -> (monthly, yearly)."""
    for year in range(2025, 1874, -1):
        if year == 2025:
            creation = "20260305"
        elif year == 2024:
            creation = "20250221"
        else:
            creation = "20240831"

        out_path = RAW_DIR / "NOAA" / f"tsi_{year}.nc"
        if out_path.exists():
            continue
        url = (
            f"https://www.ncei.noaa.gov/data/total-solar-irradiance/access/monthly/"
            f"tsi_v03r00_monthly_s{year}01_e{year}12_c{creation}.nc"
        )
        dir_exists(out_path)
        try:
            r = requests.get(url, timeout=30)
            if r.status_code == 200:
                out_path.write_bytes(r.content)
        except requests.RequestException:
            pass

    tsi_files = sorted(RAW_DIR.glob("NOAA/tsi_*.nc"))
    tsi_list = []
    for f in tsi_files:
        ds = xr.open_dataset(f)
        tsi_list.append(ds[["TSI"]].load())
        ds.close()
    tsi = xr.concat(tsi_list, dim="time")

    tsi_monthly = pd.DataFrame({"time": tsi["time"].values, "TSI": tsi["TSI"].values})
    tsi_yr = tsi["TSI"].resample(time="YE").mean()
    tsi_yearly = pd.DataFrame({"Year": tsi_yr.time.dt.year.values, "TSI": tsi_yr.values})
    return tsi_monthly, tsi_yearly


def download_epica() -> pd.DataFrame:
    """EPICA Dome C ice-core temperature record."""
    url = "https://doi.pangaea.de/10.1594/PANGAEA.683655?format=textfile"
    raw_path = RAW_DIR / "EPICA" / "epica_dome_c.txt"
    if not raw_path.exists():
        dir_exists(raw_path)
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        raw_path.write_text(r.text, encoding="utf-8")

    epica_raw = pd.read_csv(raw_path, sep="\t", skiprows=20, na_values=[""])
    epica_raw.columns = ["depth_m", "age_ka", "dD_permil", "delta_t_c", "sample_id"]
    return epica_raw.dropna(subset=["age_ka", "delta_t_c"])[["age_ka", "delta_t_c"]].copy()


def download_vostok_co2() -> pd.DataFrame:
    """Vostok/EDC3 ice-core CO2 record (age in ka before present)."""
    url = "https://www.ncei.noaa.gov/pub/data/paleo/icecore/antarctica/epica_domec/vostok-edc3-co2-2008-noaa.txt"
    raw_path = RAW_DIR / "NOAA" / "vostok-edc3-co2-2008-noaa.txt"
    if not raw_path.exists():
        dir_exists(raw_path)
        raw_path.write_text(requests.get(url).text)

    vostok_raw = pd.read_csv(raw_path, sep="\t", skiprows=482)
    vostok_raw.columns = ["depth_m", "gas_age_bp", "co2_ppm"]
    return (
        vostok_raw
        .dropna(subset=["gas_age_bp", "co2_ppm"])
        .assign(
            gas_age_bp=lambda df: pd.to_numeric(df["gas_age_bp"], errors="coerce"),
            co2_ppm=lambda df: pd.to_numeric(df["co2_ppm"], errors="coerce"),
        )
        .dropna(subset=["gas_age_bp", "co2_ppm"])
        .sort_values("gas_age_bp")
        .assign(age_ka=lambda df: df["gas_age_bp"] / 1000)
        [["age_ka", "co2_ppm"]]
    )


#================================
# Beck et al. (2023) -- Koppen-Geiger maps + 1km/0.1deg climate ensemble
#================================


def download_beck_climate_and_kg(ph_lat: tuple = (4.5, 21.5), ph_lon: tuple = (113.5, 127.0),
                                  keep_periods=("1901_1930", "1991_2020", "2071_2099")) -> dict:
    """Downloads Beck et al.'s Koppen-Geiger classification (1km) and climate ensemble (0.1deg)
    from figshare, keeps only the periods/resolutions the workshop needs, and crops to the PH bbox.

    Returns a dict of {output_name: xr.Dataset}, e.g. "kg_philippines_present.nc" -> Dataset.
    Caller decides where under data/processed/ to save each one.
    """
    FIGSHARE_ID = 21789074
    target_files = {"koppen_geiger_nc.zip", "climate_data_0p1.zip"}
    beck_dir = RAW_DIR / "Beck"
    beck_dir.mkdir(parents=True, exist_ok=True)

    resp = requests.get(f"https://api.figshare.com/v2/articles/{FIGSHARE_ID}/files")
    resp.raise_for_status()
    all_files = resp.json()

    for f in all_files:
        if f["name"] not in target_files:
            continue
        out_path = beck_dir / f["name"]
        if out_path.exists():
            continue
        r = requests.get(f["download_url"], stream=True)
        r.raise_for_status()
        with open(out_path, "wb") as fp:
            for chunk in r.iter_content(chunk_size=4 * 1024 * 1024):
                fp.write(chunk)

    for zip_name in target_files:
        extract_dir = beck_dir / zip_name.replace(".zip", "")
        if extract_dir.exists() and any(extract_dir.rglob("*.nc")):
            continue
        extract_dir.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(beck_dir / zip_name) as zf:
            zf.extractall(extract_dir)

    def _rmtree(path):
        """shutil.rmtree with read-only fix for Windows/OneDrive."""
        def _fix_readonly(func, p, _):
            os.chmod(p, stat.S_IWRITE)
            func(p)
        shutil.rmtree(path, onerror=_fix_readonly)

    # prune unwanted periods/resolutions to keep disk usage down
    for sub in ["koppen_geiger_nc", "climate_data_0p1"]:
        for d in list((beck_dir / sub).iterdir()):
            if d.is_dir() and d.name not in keep_periods:
                _rmtree(d)

    for period in ["1901_1930", "1991_2020"]:
        period_dir = beck_dir / "koppen_geiger_nc" / period
        if period_dir.exists():
            for f in period_dir.iterdir():
                if f.name != "koppen_geiger_0p00833333.nc":
                    os.chmod(f, stat.S_IWRITE)
                    f.unlink()

    for sub in ["koppen_geiger_nc", "climate_data_0p1"]:
        future_dir = beck_dir / sub / "2071_2099"
        if not future_dir.exists():
            continue
        for d in list(future_dir.iterdir()):
            if d.name != "ssp460":
                _rmtree(d)
        if sub == "koppen_geiger_nc":
            for f in (future_dir / "ssp460").iterdir():
                if f.name != "koppen_geiger_0p00833333.nc":
                    os.chmod(f, stat.S_IWRITE)
                    f.unlink()

    def crop_philippines(ds):
        lat_name = "latitude" if "latitude" in ds.coords else "lat"
        lon_name = "longitude" if "longitude" in ds.coords else "lon"
        lat = ds[lat_name].values
        if lat[0] > lat[-1]:   # decreasing (90 -> -90)
            return ds.sel({lat_name: slice(ph_lat[1], ph_lat[0]), lon_name: slice(ph_lon[0], ph_lon[1])})
        else:                   # increasing (-90 -> 90)
            return ds.sel({lat_name: slice(ph_lat[0], ph_lat[1]), lon_name: slice(ph_lon[0], ph_lon[1])})

    clim = beck_dir / "climate_data_0p1"
    targets = [
        (beck_dir / "koppen_geiger_nc/1991_2020/koppen_geiger_0p00833333.nc", "kg_philippines_present.nc"),
        (beck_dir / "koppen_geiger_nc/2071_2099/ssp460/koppen_geiger_0p00833333.nc", "kg_philippines_future_ssp460.nc"),
        (clim / "1901_1930/ensemble_mean_0p1.nc", "climate_philippines_1901_1930_mean.nc"),
        (clim / "1991_2020/ensemble_mean_0p1.nc", "climate_philippines_1991_2020_mean.nc"),
        (clim / "2071_2099/ssp460/ensemble_mean_0p1.nc", "climate_philippines_2071_2099_ssp460_mean.nc"),
    ]

    return {out_name: crop_philippines(xr.open_dataset(src)) for src, out_name in targets}


#================================
# GBIF species occurrence records
#================================


def download_gbif(taxon_key, country='PH', out_path=None):
    records, offset, limit = [], 0, 300
    base = 'https://api.gbif.org/v1/occurrence/search'
    while True:
        r = requests.get(base, params={
            'taxonKey': taxon_key, 'country': country,
            'hasCoordinate': 'true', 'hasGeospatialIssue': 'false',
            'limit': limit, 'offset': offset,
        })
        r.raise_for_status()
        data = r.json()
        records.extend(data['results'])
        if data['endOfRecords']:
            break
        offset += limit

    df = pd.DataFrame([
        {
            'species':  rec.get('species', ''),
            'lon':      rec.get('decimalLongitude'),
            'lat':      rec.get('decimalLatitude'),
            'year':     rec.get('year'),
            'basis':    rec.get('basisOfRecord', ''),
            'gbifID':   rec.get('gbifID'),
        }
        for rec in records if rec.get('decimalLongitude') is not None
    ])

    if out_path is not None:
        Path(out_path).parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(out_path, index=False)
    return df


def download_gbif_compilation(download_key: str, keep_cols: list, out_dir=None) -> pd.DataFrame:
    """Downloads a pre-assembled GBIF occurrence-download archive (a DOI-backed compilation
    of many constituent datasets, e.g. a whole-taxon/whole-country pull), extracts
    occurrence.txt, and returns it trimmed to `keep_cols`."""
    out_dir = Path(out_dir) if out_dir is not None else (RAW_DIR / "GBIF" / download_key)
    out_dir.mkdir(parents=True, exist_ok=True)
    zip_path = out_dir / f"{download_key}.zip"

    if not zip_path.exists():
        url = f"https://api.gbif.org/v1/occurrence/download/request/{download_key}.zip"
        r = requests.get(url, timeout=120)
        r.raise_for_status()
        zip_path.write_bytes(r.content)

    with zipfile.ZipFile(zip_path) as z:
        for member in ["occurrence.txt", "citations.txt", "rights.txt"]:
            if not (out_dir / member).exists():
                z.extract(member, out_dir)

    return pd.read_csv(out_dir / "occurrence.txt", sep="\t", usecols=keep_cols, low_memory=False)


#================================
# Hansen Global Forest Change -- windowed remote reads, no full-tile download
#================================


def download_hansen_tiles(bbox, tiles: list, layers: list = ("treecover2000", "lossyear"),
                           version: str = "GFC-2023-v1.11", out_dir=None) -> dict:
    """Reads only the `bbox`-sized window out of each remote Hansen tile (public GCS COGs) and
    mosaics same-layer tiles together. Returns {layer: (data, transform, profile)}; caller decides
    whether/where to save a GeoTIFF."""
    base = f"https://storage.googleapis.com/earthenginepartners-hansen/{version}"
    out_dir = Path(out_dir) if out_dir is not None else (RAW_DIR / "Hansen")
    out_dir.mkdir(parents=True, exist_ok=True)

    results = {}
    for layer in layers:
        mem_files = []
        for tile in tiles:
            url = f'{base}/Hansen_{version}_{layer}_{tile}.tif'
            with rasterio.open(url) as src:
                win = from_bounds(*bbox, src.transform)
                row0, col0 = max(0, int(win.row_off)), max(0, int(win.col_off))
                row1 = min(src.height, int(win.row_off + win.height))
                col1 = min(src.width, int(win.col_off + win.width))
                if row1 <= row0 or col1 <= col0:
                    continue
                win_c = rasterio.windows.Window(col0, row0, col1 - col0, row1 - row0)
                data = src.read(1, window=win_c)
                transform = src.window_transform(win_c)
                profile = src.profile.copy()
                profile.update(width=data.shape[1], height=data.shape[0], transform=transform, count=1)
            mem = MemoryFile()
            with mem.open(**profile) as mds:
                mds.write(data, 1)
            mem_files.append(mem)

        if not mem_files:
            continue
        opened = [m.open() for m in mem_files]
        mosaic, out_transform = rio_merge(opened)
        profile_out = opened[0].profile.copy()
        profile_out.update(height=mosaic.shape[1], width=mosaic.shape[2], transform=out_transform, count=1)
        for d in opened:
            d.close()
        for m in mem_files:
            m.close()

        out_path = out_dir / f'hansen_{layer}.tif'
        with rasterio.open(out_path, 'w', **profile_out) as dst:
            dst.write(mosaic[0], 1)
        results[layer] = out_path

    return results


def build_hansen_mosaic(bbox, tiles: list, target_lat: np.ndarray, target_lon: np.ndarray,
                         layer: str = "treecover2000", version: str = "GFC-2023-v1.11") -> np.ndarray:
    """Aggregates a Hansen Global Forest Change layer onto an existing target grid via windowed +
    decimated remote reads -- no reprojection needed (both source and target are plain lat/lon), and
    no native ~30 m file is ever written to disk.

    Unlike the Copernicus DEM tiles in `build_dem_mosaic`, Hansen's public GeoTIFFs are row-strip
    organized (not internally tiled, no overviews) -- a decimated read still has to fetch and
    decompress every full-width row in the requested window, just fewer of them. So the window is
    restricted to `bbox` explicitly (not the whole 10x10 degree tile) to avoid paying for area outside
    the region actually needed. Expect roughly 1-2 minutes per tile with substantial bbox overlap.
    """
    base = f"https://storage.googleapis.com/earthenginepartners-hansen/{version}"
    mosaic = np.full((len(target_lat), len(target_lon)), np.nan, dtype="float32")

    for tile in tiles:
        url = f"{base}/Hansen_{version}_{layer}_{tile}.tif"
        with rasterio.open(url) as src:
            left, bottom, right, top = src.bounds
            win_bounds = (max(left, bbox[0]), max(bottom, bbox[1]), min(right, bbox[2]), min(top, bbox[3]))
            if win_bounds[0] >= win_bounds[2] or win_bounds[1] >= win_bounds[3]:
                continue   # this tile doesn't overlap bbox at all
            cols = np.where((target_lon >= win_bounds[0]) & (target_lon < win_bounds[2]))[0]
            rows = np.where((target_lat <= win_bounds[3]) & (target_lat > win_bounds[1]))[0]
            if len(cols) == 0 or len(rows) == 0:
                continue
            win = from_bounds(*win_bounds, src.transform)
            out_shape = (len(rows), len(cols))
            data = src.read(1, window=win, out_shape=out_shape, resampling=Resampling.average)
        r0, r1 = rows.min(), rows.max() + 1
        c0, c1 = cols.min(), cols.max() + 1
        mosaic[r0:r1, c0:c1] = data.astype("float32")

    return mosaic


#================================
# Multispectral composites (Sentinel-2 / Landsat) -- cloud-masked temporal median on a common grid
#================================


def _read_band_on_grid(href, resampling, bbox, grid_shape, grid_transform, grid_crs, target_res_m):
    """Fast windowed + decimated native-CRS read (uses each COG's built-in overviews), then a
    cheap in-memory reproject of the already-small result onto the shared output grid."""
    grid_height, grid_width = grid_shape
    with rasterio.open(href) as src:
        t = Transformer.from_crs("EPSG:4326", src.crs, always_xy=True)
        xmin, ymin = t.transform(bbox[0], bbox[1])
        xmax, ymax = t.transform(bbox[2], bbox[3])
        win = from_bounds(xmin, ymin, xmax, ymax, src.transform).intersection(
            rasterio.windows.Window(0, 0, src.width, src.height))
        if win.width <= 0 or win.height <= 0:
            return None
        decim = max(1, round(target_res_m / src.res[0]))
        out_h = max(1, int(win.height / decim))
        out_w = max(1, int(win.width / decim))
        data = src.read(1, window=win, out_shape=(out_h, out_w), resampling=resampling)
        win_transform = src.window_transform(win)
        native_transform = win_transform * rasterio.Affine.scale(win.width / out_w, win.height / out_h)
        src_crs, src_nodata = src.crs, (src.nodata if src.nodata is not None else 0)

    dst = np.full((grid_height, grid_width), np.nan, dtype="float32")
    reproject(source=data.astype("float32"), destination=dst,
              src_transform=native_transform, src_crs=src_crs, src_nodata=src_nodata,
              dst_transform=grid_transform, dst_crs=grid_crs, dst_nodata=np.nan,
              resampling=resampling)
    return dst


def _composite_period(items, band_assets, qc_asset, is_clear_fn, bbox, grid_shape, grid_transform,
                       grid_crs, target_res_m, scale=1.0, offset=0.0, label=""):
    """Per-pixel cloud/shadow-masked temporal median composite across all pooled scenes."""
    n = len(items)
    grid_height, grid_width = grid_shape
    stacks = {b: np.full((n, grid_height, grid_width), np.nan, dtype="float32") for b in band_assets}
    for i, it in enumerate(items):
        qc = _read_band_on_grid(it.assets[qc_asset].href, Resampling.nearest, bbox, grid_shape,
                                 grid_transform, grid_crs, target_res_m)
        if qc is None:
            continue
        clear = is_clear_fn(np.nan_to_num(qc, nan=0).astype("uint16"))
        for band, asset_key in band_assets.items():
            data = _read_band_on_grid(it.assets[asset_key].href, Resampling.average, bbox, grid_shape,
                                       grid_transform, grid_crs, target_res_m)
            if data is not None:
                stacks[band][i] = np.where(clear, data * scale + offset, np.nan)
    with np.errstate(all="ignore"):
        return {b: np.nanmedian(s, axis=0) for b, s in stacks.items()}


def search_seasonal_scenes(bbox, s2_years: range, l5_years: range,
                            season=("02-01", "04-30"), s2_cloud_lt=60, l5_cloud_lt=70):
    """Pools Sentinel-2 L2A (recent) + Landsat 5 TM (historical) STAC items over the same
    calendar season across multiple years, so a temporal-median composite isn't biased by
    season while still averaging out clouds/shadows."""
    catalog = pystac_client.Client.open("https://earth-search.aws.element84.com/v1")
    s2_items = []
    for year in s2_years:
        search = catalog.search(collections=["sentinel-2-l2a"], bbox=bbox,
                                 datetime=f"{year}-{season[0]}/{year}-{season[1]}",
                                 query={"eo:cloud_cover": {"lt": s2_cloud_lt}}, max_items=300)
        s2_items.extend(search.items())

    pc_catalog = pystac_client.Client.open(
        "https://planetarycomputer.microsoft.com/api/stac/v1", modifier=planetary_computer.sign_inplace)
    l5_items = []
    for year in l5_years:
        search = pc_catalog.search(collections=["landsat-c2-l2"], bbox=bbox,
                                    datetime=f"{year}-{season[0]}/{year}-{season[1]}",
                                    query={"platform": {"in": ["landsat-5"]},
                                           "landsat:collection_category": {"in": ["T1"]},
                                           "eo:cloud_cover": {"lt": l5_cloud_lt}},
                                    max_items=100)
        l5_items.extend(search.items())
    return s2_items, l5_items


def build_landsat_sentinel_composite(bbox, s2_items, l5_items, target_res_m=100) -> dict:
    """Builds cloud/shadow-masked temporal-median composites for both sensors on one shared
    lat/lon grid at `target_res_m`. Returns {"s2": {...}, "l5": {...}, "grid": {...}} where each
    sensor entry has red/green/blue/nir 2-D arrays and "grid" has the LAT/LON coordinate arrays."""
    deg_per_m = 1 / 111_320
    grid_res = target_res_m * deg_per_m
    grid_width = int(round((bbox[2] - bbox[0]) / grid_res))
    grid_height = int(round((bbox[3] - bbox[1]) / grid_res))
    grid_transform = rasterio.Affine(grid_res, 0, bbox[0], 0, -grid_res, bbox[3])
    grid_crs = "EPSG:4326"
    lon = bbox[0] + grid_res * (np.arange(grid_width) + 0.5)
    lat = bbox[3] - grid_res * (np.arange(grid_height) + 0.5)
    grid_shape = (grid_height, grid_width)
    common_kwargs = dict(bbox=bbox, grid_shape=grid_shape, grid_transform=grid_transform,
                          grid_crs=grid_crs, target_res_m=target_res_m)

    # Sentinel-2 L2A: SCL classes 4/5/6 = vegetation / bare soil / water
    s2_bands = {"red": "red", "green": "green", "blue": "blue", "nir": "nir"}
    s2_clear = lambda scl: np.isin(scl, [4, 5, 6])
    s2_composite = _composite_period(s2_items, s2_bands, "scl", s2_clear, scale=1 / 10000,
                                      label="S2", **common_kwargs)

    # Landsat 5 TM: QA_PIXEL bit 6 = "clear"
    l5_bands = {"red": "red", "green": "green", "blue": "blue", "nir": "nir08"}
    l5_clear = lambda qa: ((qa.astype(np.uint16) >> 6) & 1).astype(bool)
    l5_composite = _composite_period(l5_items, l5_bands, "qa_pixel", l5_clear, scale=0.0000275,
                                      offset=-0.2, label="L5", **common_kwargs)

    return {"s2": s2_composite, "l5": l5_composite, "grid": {"lat": lat, "lon": lon}}


#================================
# WorldClim 2.1 bioclimatic variables -- cropped straight out of the remote zip
#================================


def download_worldclim_bioclim(bio_num: int, bbox, resolution: str = "30s",
                                base_url: str = "https://geodata.ucdavis.edu/climate/worldclim/2_1/base") -> xr.DataArray:
    """Crops one WorldClim 2.1 bioclim variable to `bbox` via GDAL's /vsizip/vsicurl/ -- only the
    bbox rows are transferred over HTTP range requests, never the full multi-GB global zip."""
    path = f'/vsizip/vsicurl/{base_url}/wc2.1_{resolution}_bio.zip/wc2.1_{resolution}_bio_{bio_num}.tif'
    with rasterio.open(path) as src:
        win = from_bounds(*bbox, src.transform)
        data = src.read(1, window=win).astype('float32')
        transform = src.window_transform(win)
        nodata = src.nodata
    if nodata is not None:
        data = np.where(data == nodata, np.nan, data)
    h, w = data.shape
    lon = transform.c + transform.a * (np.arange(w) + 0.5)
    lat = transform.f + transform.e * (np.arange(h) + 0.5)
    return xr.DataArray(data, coords={'lat': lat, 'lon': lon}, dims=('lat', 'lon'), name=f'bio{bio_num}')


#================================
# Copernicus DEM GLO-30 -- aggregated onto an existing target grid, native tiles never saved
#================================


def build_dem_mosaic(bbox, target_lat: np.ndarray, target_lon: np.ndarray) -> np.ndarray:
    """Searches cop-dem-glo-30 over `bbox` and block-averages each ~30m tile directly onto
    (target_lat, target_lon) via windowed+decimated remote reads -- no reprojection needed since
    both source and target are plain lat/lon, and no native-resolution file is ever written to disk."""
    cat = pystac_client.Client.open("https://planetarycomputer.microsoft.com/api/stac/v1",
                                     modifier=planetary_computer.sign_inplace)
    items = list(cat.search(collections=['cop-dem-glo-30'], bbox=list(bbox), max_items=500).items())

    dem = np.full((len(target_lat), len(target_lon)), np.nan, dtype='float32')
    for item in items:
        href = item.assets['data'].href
        with rasterio.open(href) as src:
            left, bottom, right, top = src.bounds
            cols = np.where((target_lon >= left) & (target_lon < right))[0]
            rows = np.where((target_lat <= top) & (target_lat > bottom))[0]
            if len(cols) == 0 or len(rows) == 0:
                continue
            out_shape = (len(rows), len(cols))
            data = src.read(1, out_shape=out_shape, resampling=Resampling.average)
        r0, r1 = rows.min(), rows.max() + 1
        c0, c1 = cols.min(), cols.max() + 1
        dem[r0:r1, c0:c1] = data.astype('float32')

    return dem
