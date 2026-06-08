# actually, let me go ahead and download from Copernicus API
# bounding box for the Philippines (roughly):
N_lat, S_lat, W_lon, E_lon = 21.25, 4.5, 114, 126.75

from workshop_utils import RAW_DIR
from workshop_utils.download import download_era5_copernicus

# download in single year increments
for year in range(1940, 2025):
    download_era5_copernicus(
        variable=["2m_temperature"],
        year=[str(year)],
        month=[f"{i:02d}" for i in range(1, 13)],
        day=[f"{i:02d}" for i in range(1, 32)],
        time=[f"{i:02d}:00" for i in range(0, 24, 6)],
        area=[N_lat, W_lon, S_lat, E_lon],
        output_path=RAW_DIR / "ERA5" / "2m_temperature" / f"t2m_philippines_{year}.nc",
    )