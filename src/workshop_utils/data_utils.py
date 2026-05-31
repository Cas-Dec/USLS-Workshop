"""
Data utilities.
"""


#================================
# Imports
#================================


import os
import ee
import glob
import requests
import pandas as pd
import xarray as xr
import rioxarray


#================================
# Global variables
#================================


_CURRENT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
_ARCO_DS = None
_eBird_API_KEY = "1i5hmt4s8350"


#================================
# Data loading
#================================


def launch_ARCO_ERA5():
    global _ARCO_DS
    if _ARCO_DS is None:
        print("\nConnecting to ARCO-ERA5...")
        _ARCO_DS = xr.open_zarr(
            'gs://gcp-public-data-arco-era5/ar/full_37-1h-0p25deg-chunk-1.zarr-v3',
            chunks=None,
            storage_options=dict(token='anon'),
        )
        print("Done!\n")
    return _ARCO_DS


def download_var(var, timestamp):
    """Writes out ARCO-ERA5 variable at timestamp to netCDF file."""
    _out_dir = os.path.join(_CURRENT_DIRECTORY, '..', 'data', 'ERA5', 't2m')
    _out_file =  os.path.join(_out_dir, f'{var}_{timestamp.strftime("%Y-%m-%dT%H")}.nc')
    os.makedirs(_out_dir, exist_ok=True)

    if not os.path.exists(_out_file):
        arco = launch_ARCO_ERA5()
        var_data = arco[var].sel(time=timestamp).compute()\
            .rename({"time": "valid_time"})
        var_data.to_netcdf( _out_file)


def load_lsm():
    lsm_path = os.path.join(_CURRENT_DIRECTORY, '..', 'data', 'ERA5', 'landseamask.nc')
    if not os.path.exists(lsm_path):
        print("[WARNING]: Downloading land-sea mask on the fly...")
        download_var("lsm", '2024-01-01T00') # arbitrary timestamp
        
    landseamask = xr.open_dataset(lsm_path)
    return landseamask


def request_eBird():

    region = "PH"
    species = "cangoo"

    url = f"https://api.ebird.org/v2/data/obs/{region}/recent"
    headers = {
        "X-eBirdApiToken": _eBird_API_KEY
    }
    r = requests.get(url, headers=headers)
    
    if r.status_code == 200:
        return r.json()
    else:
        raise Exception(f"eBird API request failed with status code {r.status_code}: {r.text}")


# --- region: Negros (approx bbox) ---
def get_negros_geometry():
    return ee.Geometry.Rectangle([122.5, 9.0, 123.5, 11.0])


# --- generic downloader ---
def ee_download(_collection="ECMWF/ERA5/MONTHLY",
                _var="mean_2m_air_temperature",
                start="2000-01-01",
                end="2020-12-31",
                scale=10000,
                reducer=ee.Reducer.mean(),
                fname=None):

    region = get_negros_geometry()

    col = (
        ee.ImageCollection(_collection)
        .select(_var)
        .filterDate(start, end)
        .filterBounds(region)
    )

    def reduce_image(img):
        stat = img.reduceRegion(
            reducer=reducer,
            geometry=region,
            scale=scale,
            bestEffort=True
        )
        date = ee.Date(img.get("system:time_start")).format("YYYY-MM-dd")
        return ee.Feature(None, {
            "date": date,
            _var: stat.get(_var)
        })

    fc = col.map(reduce_image)

    # pull to client (OK since it's just time series)
    data = fc.getInfo()["features"]

    df = pd.DataFrame([
        {
            "date": f["properties"]["date"],
            _var: f["properties"][_var]
        }
        for f in data
    ])

    df["date"] = pd.to_datetime(df["date"])

    if fname is None:
        fname = f"{_collection.replace('/', '_')}_{_var}.csv"

    _path = os.path.join(_CURRENT_DIRECTORY, '..', 'data', 'EE')
    os.makedirs(_path, exist_ok=True)
    out = os.path.join(_path, fname)
    df.to_csv(out, index=False)

    return df


def ee_export_collection(_collection="ECMWF/ERA5_LAND/MONTHLY_AGGR",
                         _var="mean_2m_air_temperature",
                         start="2000-01-01",
                         end="2020-12-31",
                         scale=10000,
                         region=None,
                         folder="EE_exports"):

    ee.Initialize()

    if region is None:
        region = ee.Geometry.Rectangle([122.5, 9.0, 123.5, 11.0])  # Negros

    col = (ee.ImageCollection(_collection)
           .select(_var)
           .filterDate(start, end)
           .filterBounds(region))

    col_list = col.toList(col.size())

    n = col.size().getInfo()

    for i in range(n):
        img = ee.Image(col_list.get(i))
        date = ee.Date(img.get("system:time_start")).format("YYYYMM").getInfo()

        task = ee.batch.Export.image.toDrive(
            image=img,
            description=f"{_var}_{date}",
            folder=folder,
            fileNamePrefix=f"{_var}_{date}",
            region=region,
            scale=scale,
            maxPixels=1e13
        )
        task.start()


def tifs_to_netcdf(path_pattern, out_file):
    files = sorted(glob.glob(path_pattern))

    datasets = []
    for f in files:
        da = rioxarray.open_rasterio(f)
        da = da.squeeze("band", drop=True)
        datasets.append(da)

    ds = xr.concat(datasets, dim="time")
    ds.to_netcdf(out_file)