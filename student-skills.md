# Student Skills Tracker

Tracks what students have hands-on experience with, notebook by notebook, so later days can build on (and not re-teach) prior skills. Update this after each day's notebook is finalized.

---

## Day 1 — `notebooks/day1.ipynb`

Theme: global temperature record, climate drivers (sun, volcanoes, ENSO, CO₂), Philippines/Bacolod climate, Köppen-Geiger classification.

### Python basics (no library)
- Variables and assignment (`my_name = "Cas"`)
- `type()` to inspect a variable's type
- Strings and **f-strings** for interpolation (`f"Hello {name}"`)
- `print()` for inspecting values/dataframes
- `if / elif / else` decision trees, incl. compound conditions with `and` / `or`
- Indexing basics: zero-based indexing (`axes[0]`, not `axes[1]`, for the first item)
- `range(1, 13)` for iterable ranges
- Mentioned only conceptually, not yet used directly: `functions`, `classes`

### numpy (`np`)
- `np.linspace(start, stop, n)` — generate evenly spaced arrays
- `np.random.normal(mean, std, n)` — synthetic noisy data for smoothing demos
- `np.polyfit(x, y, deg)` / `np.polyval(coeffs, x)` — linear trend fitting (used for Bacolod's warming-per-decade trend)
- Basic array arithmetic (`2 * x + 1`, `x**2`, `np.sin(x)`)

### pandas (`pd`)
- `pd.read_csv(path)` — reading tabular `.csv` data (BEST, GISTEMP, TSI, AOD, ENSO, CO₂, EPICA, Vostok datasets)
- `pd.read_csv(path, parse_dates=[...])` — parsing date columns (used for monthly TSI)
- `.head(n)` — preview first rows
- Column access via `df["colname"]`, `.columns`
- `.min()` / `.max()` on a column (e.g., first/last year of a record)
- `pd.Series(...)` — wrapping a raw array as a pandas Series
- `.rolling(window=n, center=True).mean()` — moving average / smoothing, incl. experimenting with different `window` sizes
- `df.merge(other, left_on=..., right_on=..., how="inner")` — merging two datasets on a shared key (CO₂ + BEST temperature merge for scatter plot)
- Implicitly: dataframe vs. column vs. `.values` (numpy array) distinction

### matplotlib (`plt`)
Core plotting mechanics — students got heavy repeated practice here across many exercises:
- `fig, ax = plt.subplots(figsize=(w, h))` — single-axes figures
- `fig, axes = plt.subplots(nrows, ncols, figsize=..., sharex=True/False)` — multi-panel subplots, indexing `axes[0]`, `axes[1]`
- `ax.plot(x, y, color=..., linewidth=..., linestyle=..., alpha=..., label=...)` — line plots, styling
- `ax.axhline(y, color=..., linewidth=..., linestyle=...)` / `ax.axvline(...)` — reference lines (zero lines, eruption years, ppm thresholds)
- `ax.fill_between(x, y1, y2=0, where=condition, color=..., alpha=...)` — shading areas, incl. conditional shading above/below zero (El Niño/La Niña, warm/cold ice-core periods)
- `ax.set_title()`, `ax.set_xlabel()`, `ax.set_ylabel()`, `ax.legend()`
- `ax.set_xlim()` / `ax.set_ylim()`, including **reversing an axis** (`set_xlim(max, min)`) for "age before present" data
- `ax.text(x, y, "label", color=..., fontsize=..., rotation=...)` — annotations
- `ax.twinx()` — secondary y-axis for dual-variable plots (TSI vs temp, CO₂ vs temp)
- Combining legends from two axes (`get_legend_handles_labels()` + concatenation)
- `ax.bar(...)` — bar charts (monthly precipitation)
- `ax.scatter(x, y, c=..., cmap=..., s=..., edgecolors=..., alpha=...)` + `plt.colorbar()` — scatter with color-mapped third variable
- `ax.set_xticks()` / `ax.set_xticklabels()` — custom tick labels (month names)
- `plt.suptitle()` — figure-level title vs. per-axes title
- `ax.set_aspect("equal")` — for geographic maps
- `plt.tight_layout()`, `plt.show()`
- `mcolors.ListedColormap(...)`, `mcolors.BoundaryNorm(...)` — discrete/categorical colormaps (Köppen-Geiger classes)
- `mpatches.Patch(...)` — building custom legend handles for categorical maps
- `ax.contour(x, y, z, levels=..., colors=..., linewidths=...)` — contour lines (land-sea mask outline)
- `ax.pcolormesh(x, y, z, cmap=..., norm=...)` — 2D categorical raster plotting (KG climate maps)
- Colormap names encountered: `RdYlBu_r`, `YlGnBu`, `viridis`, plus manual discrete colormaps

### xarray (`xr`)
- Reading `.nc` (NetCDF) files: `xr.open_dataarray(path)` vs `xr.open_dataset(path)`
- Concept: `Dataset` (multiple variables) vs `DataArray` (single variable); indexing a `Dataset` by variable name (`ds["t2m"]`)
- Inspecting coordinates: `da.latitude`, `da["latitude"]`, `da.coords["latitude"]`, `.values` to get raw numpy array
- `da.plot()` — xarray's built-in quick-plot, and passing `ax=` to route into a matplotlib axes for styling (`cmap`, `vmin`, `vmax`)
- `.squeeze()` — dropping singleton dimensions (used before plotting KG classification maps)
- `list(ds.data_vars)` — introspecting variable names in a Dataset
- Basic aggregation via `.min()`, `.max()`, `.sum()` on a DataArray (used for Köppen-Geiger criteria: coldest/warmest month, annual precip, driest month)

### workshop_utils (project-internal package)
- `from workshop_utils import RAW_DIR, PROCESSED_DIR` — path constants abstracting away file locations
- Students only ever read from `PROCESSED_DIR`, never `RAW_DIR`, in Day 1

### Domain/conceptual content (not code skills, but shapes what Day 2/3 can assume as background knowledge)
- Temperature anomalies vs. absolute temperature, reference periods
- Global temperature drivers: solar irradiance/sunspots, volcanic aerosols, ENSO (Niño 3.4 index), CO₂/greenhouse effect
- Correlation vs. causation reasoning
- Ice-core paleoclimate records (EPICA temperature, Vostok CO₂)
- Köppen-Geiger climate classification (decision-tree logic, main groups A–E, subtypes Af/Am/Aw)
- ERA5 reanalysis concept, gridded/geospatial climate data
- Philippines/Bacolod-specific framing (typhoons, sea level rise, monsoon rainfall pattern)

---

## Day 2 — `notebooks/day2.ipynb`
*(Parts I-II reviewed; Parts III-IV not yet built)*

Theme: building a homemade Köppen-Geiger classifier from scratch (Part I), then the Philippines as a biodiversity hotspot — forest cover, satellite imagery, fauna (Part II).

### Python basics (no library)
- `def` functions with multiple parameters and a `return` statement (first real hands-on use; only mentioned conceptually in Day 1)
- `for` loops over a list, incl. unpacking tuples (`for name, price in prices`)
- **Nested `for` loops** over 2D grid indices (`for i in range(...): for j in range(...):`), incl. `continue` to skip an iteration
- List/array slicing (`monthly_P[3:9]`) to pull out a sub-range (e.g. Apr-Sep from 12 months)
- Dictionaries for lookup tables (`GROUP_TO_KG_CODE[climate_code]`)
- `np.argmin(np.abs(array - value))` — finding the closest value's index in an array

### numpy (`np`)
- `np.full(shape, fill_value)` — pre-allocating an output array (e.g. NaN-filled grid before a loop fills it in)
- `np.dstack([...])` — stacking 2D arrays into a 3D `(rows, cols, channels)` image array
- `np.nan_to_num(...)` — replacing NaNs with a fixed value (e.g. before building an RGB image)
- `.astype(np.uint8)` — casting array dtype
- Boolean arrays + `.mean()` as a "fraction true" trick (`(array > threshold).mean()`), used for both raster stats and pandas null-rate checks

### pandas (`pd`)
- `.value_counts()` — frequency counts of a categorical column
- `.isnull().sum()` / `.isnull().mean()` — data-quality / null-rate checks before filtering or plotting
- `.str.contains(text, case=False, na=False)` — partial text matching for filtering (messy real-world category columns, e.g. `stateProvince` variants like "Negros Oriental"/"Negros I")
- Boolean filtering via a named condition variable (`df[is_negros]`), building on Day 1's inline `df[condition]`
- A pandas `Series.plot()`/`.value_counts()` combo feeding directly into a bar chart

### matplotlib (`plt`)
- `ax.imshow(rgb_array)` — displaying a `(rows, cols, 3)` array as a true-colour image (first non-data-map image display)
- `ax.axis("off")` — hiding axes for photo-like images
- Reused without new teaching: `pcolormesh` + discrete colormap/legend pattern (Köppen maps), `contour` (land-sea mask outlines), multi-panel subplots, scatter, bar charts

### xarray (`xr`)
- Genuinely 3D datasets (`time, lat, lon`) vs. Day 1's already-time-reduced 2D climatologies
- `.coarsen(dim1=n, dim2=n, boundary="trim").mean()` — downsampling a high-resolution raster for faster plotting
- `da.plot()` on a large raster with `cbar_kwargs` for colorbar label customization
- `.sel(time="2024-04-03")` — label-based selection along a non-lat/lon dimension

### Domain/conceptual content
- Full Köppen-Geiger decision tree incl. rigorous aridity threshold (Peel, Finlayson & McMahon 2007 formula, using seasonal precipitation distribution) — not just the Day 1 simplified/placeholder version
- Multispectral satellite imagery: bands vs. true colour, NDVI concept (red/nir), Sentinel-2 mission basics
- Hansen Global Forest Change dataset (treecover2000)
- GBIF occurrence data structure and quirks (sparse/clustered records, geocoding errors, missing values)
- IUCN Red List categories (LC/NT/VU/EN/CR/DD)

### workshop_utils / data
- `land_sea_mask_0p1.nc` — a second land-sea mask (0.1°, matches the Beck climate grid), distinct from Day 1's ERA5-resolution `land_sea_mask.nc`
- Data lives partly under `PROCESSED_DIR / "day_2"` (GBIF CSVs, Sentinel-2, Hansen forest change) vs. directly under `PROCESSED_DIR` (climate/KG files, reused from Day 1)

## Day 3 — `notebooks/day3.ipynb`
*(not yet reviewed — populate after auditing day3.ipynb)*
