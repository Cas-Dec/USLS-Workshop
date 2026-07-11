# What to change in @notebooks/d2p3.ipynb

I'd create the following subsections:

## Where has forest been lost?

Looking good. Starting with a full negros image from the Hansen forest loss, then computing how much loss there has been between 2001-2023. Keep as is.

## Zooming in: Guimaras.

Here, I would first again start with Hansen forest cover & loss, identical plot to above, but cropped to GUIMARAS_BBOX = dict(longitude=slice(122.46, 122.75), latitude=slice(10.76, 10.40)).

Then, the cell that's already there, computing the 3.1% loss fraction as compared to Negros' overall 1.5% - good.

In the satellite imagery, instead of the whole of Guimaras, we can do a 1x3 subplot. Left: full-Guimaras Hansen forest loss plot with bbox indicating where we'll zoom. Then, from guimaras_zoom_imagery.nc, middle Landsat 5 and right Sentinel-2 RGB: can the students spot forest loss from satellite true color imagery by eye?

## NDVI: from satellite bands to vegetation mapping

Start with 2x3 subplot, Negros-level: Hansen forest cover, visual_r, visual_g, visual_b, red, nir, the latter 5 all from negros_imagery.nc, of course. Ask the students: which band reflects best the forest cover pattern from Hansen? Can we identify forest from one band only?

NDVI composite for Negros, looks good the way it is implemented. I also like the 1x4 subplot comparing the Hansen forest cover and then different NDVI threshold maps: clearly shows how strongly NDVI is linked to vegetation.

## From NDVI to land-cover mapping

Here, I'd first go again to the very high resolution guimaras_zoom_imagery.nc, just for the sentinel-2, do land cover mapping. Compare land cover maps to Sentinel-2 image. Ask students: does it look good?

Landsat versus Sentinel land cover classes: for the guimaras_zoom_imagery.nc, apply the land cover classification and compare between the two satellite products.

## Land Use Change

Here, we look at guimaras_imagery.nc, which has 30m red/nir bands for the whole island. Start by calibrating the brightness / whatever differences between Landsat 5 and Sentinel-2. Then, do the land cover mapping, compare forest loss for NDVI threshold of 0.7 for forest with the Hansen forest loss.

Culminate with land use change map for the entire Negros using the 200m resolution negros_imagery.nc.