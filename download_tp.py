# actually, let me go ahead and download from Copernicus API
# bounding box for the Philippines (roughly):
N_lat, S_lat, W_lon, E_lon = 21.25, 4.5, 114, 126.75

from workshop_utils import RAW_DIR
from workshop_utils.download import download_era5_copernicus

# download in single year increments
for year in range(2025, 1940, -1):
    outfile=RAW_DIR / "ERA5" / "precipitation" / f"tp_philippines_{year}.nc"
    if not outfile.exists():
        download_era5_copernicus(
            dataset = "derived-era5-single-levels-daily-statistics",
            variable=["total_precipitation"],
            year=[str(year)],
            month=[f"{i:02d}" for i in range(1, 13)],
            day=[f"{i:02d}" for i in range(1, 32)],
            daily_statistic="daily_sum",
            time_zone="utc+08:00",
            frequency="1_hourly",
            area=[N_lat, W_lon, S_lat, E_lon],
            output_path=outfile,
        )
    else:
        print(f"{year} exists.")