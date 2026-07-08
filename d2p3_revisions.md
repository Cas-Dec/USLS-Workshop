# What to change in @notebooks/d2p3.ipynb

START with a plot of Hansen forest loss over Negros. There seems to be a lot of forest loss on Guimaras island, let's zoom in there. What the students see: land use change.

THEN visualize Landsat (1988-2000) - Sentinel 2 (2022-2024) composites over the same area, with maximum resolution (did we keep Sentinel 2 at native res or did we regrid it already? For this visual, zooming in, it would be best to have resolution as high as possible)

NARRATIVE: we observe land use change, but it's hard to delineate by eye from the satellite imagery. But how can we actually track that over large areas at once? That's the motivation for land use classification.

BUT there's a problem in our data: the landsat composite has NaNs practically over all of the ocean. Why is that, did something go wrong in data processing? Check @behind-the-scenes/day2_bts.ipynb . Can't we get a better quality landsat composite? Either way, if it works well over land that's fine, then we just have to make sure we use the land sea mask throughout the notebook to work only over land.

BEFORE we move over to NDVI, quick 1x4 subplot of Hansen forest cover - Sentinel 2 visual r - Sentinel 2 visual g - Sentinel 2 visual b. Ask students what they notice in the different bands. Is one band better for detecting forest cover than another?

THEN move over to NDVI. That section is nice, also the section moving over to land cover classes.

Calibrating brightness across sensors using the ocean is a bad idea as the Landsat composite has mostly NaNs over oceans across its visual bands.

The land use change starting with forest cover loss is something I would do at the start of this notebook, see above. The binary forest loss plot is very ugly. It doesn't need a colormap.

These are enough changes to implement for now.