# download.py - functions to download data from the web

# imports
import cdsapi
from workshop_utils import RAW_DIR, PROCESSED_DIR
from workshop_utils.data_utils import dir_exists

# downloading ERA5 from Copernicus Climate Data Store (CDS)
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