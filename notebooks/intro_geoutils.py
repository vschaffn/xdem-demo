# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.14.0
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# # Manipulating raster/vector data with geoutils

# xdem relies on a second library, developed by the same group of people, to easily handle raster and vector data: **geoutils !**

# ### Import the necessary modules

# +
import matplotlib.pyplot as plt
import numpy as np

import geoutils as gu
import xdem
# -

# ### Download the sample data set (if not done already) - Should take a few seconds ###

xdem.examples.download_longyearbyen_examples(overwrite=False)
print(xdem.examples.FILEPATHS_DATA["longyearbyen_ref_dem"])
print(xdem.examples.FILEPATHS_DATA["longyearbyen_tba_dem"])
print(xdem.examples.FILEPATHS_DATA["longyearbyen_glacier_outlines"])

# ### Read the two DEMs and glacier outlines for the region ###

# Raster files (e.g. GeoTiff) can be loaded in one line with `gu.Raster(path_to_file)`. In xdem, the DEM class inherit the same functionalities and more, so here we use `xdem.DEM`.

dem_2009 = xdem.DEM(xdem.examples.FILEPATHS_DATA["longyearbyen_ref_dem"])
dem_1990 = xdem.DEM(xdem.examples.FILEPATHS_DATA["longyearbyen_tba_dem"])

# Vector files (e.g. ESRI shapefiles) can be loaded in one line with `gu.Vector(path_to_file)`.

outlines_1990 = gu.Vector(xdem.examples.FILEPATHS_DATA["longyearbyen_glacier_outlines"])

# ### Quickly visualize a raster
# Since a Raster object comes with all atributes, it can be quickly plot with its georeferencing information.

dem_2009.show()

# It is easier to visualize as a hillshade

dem_2009_hs = xdem.terrain.hillshade(dem_2009)
dem_2009_hs.show(cmap='gray')

# ### Quickly visualize vector data

outlines_1990.ds.plot()

# ### Notes on the Raster and Vector classes
#
# #### The `xdem.DEM` instances inherit from the `geoutils.Raster` class, which is based upon **rasterio**. 
# These objects contain the raster metadata, with the same convention as rasterio. 
# To georeference an object, one needs to know the coordinate reference system (called `crs` in rasterio/geopandas) and any 3 of these four information:
# - the raster width and height
# - the pixel resolution
# - the extent of the raster (called `bounds` in rasterio/geopandas)
# - the position of one pixel, traditionally, the upper-left
# These variables are inter-dependent, e.g. if one knows the raster's extent and width and height, the pixel resolution is fixed.
# All these variables are stored in the `xdem.DEM` instance with the following attributes:

print(dem_2009.crs.to_proj4()); print(dem_2009.crs.to_wkt())

dem_2009.width

dem_2009.height

dem_2009.res

dem_2009.bounds

# The resolution and position of the upper left pixel are traditionally stored in a so-called [transform](https://rasterio.readthedocs.io/en/latest/topics/transforms.html):

dem_2009.transform

# These information, and more, can all be obtained **at once** with the command

print(dem_2009)

# or similarly with `dem_2009.info()`.
#
# Along with these metadata, the `xdem.DEM` object contains the data, stored as a numpy masked array in the `self.data` attribute:

dem_2009.data

# #### `gu.Vector` instances are based upon geopandas. 
# The class contains several useful methods (`self.create_mask` is showcased below), and the GeoDataFrame can accessed via:

outlines_1990.ds

# ## Rasters operations

# ### Reproject the two DEMs on the same grid

dem_1990 = dem_1990.reproject(dst_ref=dem_2009)
print(dem_1990)
print(dem_2009)

# ### Reproject to a given resolution, bounds, or CRS

dem_test = dem_1990.reproject(dst_res=60)
print(dem_test.info())

dem_test = dem_1990.reproject(dst_bounds={"left":502810, "top":8674000, "right":529430, "bottom": 8654290})
print(dem_test.info())

dem_test = dem_1990.reproject(dst_crs='epsg:4326')
print(dem_test.info())

# ### Reproject the outlines in the same coordinate system as DEMs

outlines_proj = gu.Vector(outlines_1990.ds.to_crs(dem_2009.crs))

# ### Calculate the elevation change

ddem = dem_2009 - dem_1990

# ### Plot the elevation change map
# #### Note: 
# - `ax` is used here the share the same subplot between the raster and outlines (the default is to create a new figure) 
# - ddem is plotted last, to preserve the extent, as glacier outlines cover all of Svalbard.
# - zorder is used to plot in the right sequence (outlines on top)

# +
vmax = max(abs(np.max(ddem.data)), abs(np.min(ddem.data)))

ax = plt.subplot(111)
outlines_proj.ds.plot(ax=ax, facecolor='none', edgecolor='k', zorder=2)
ddem.show(ax=ax, cmap='RdYlBu', vmin=-vmax, vmax=vmax, cb_title='Elevation change 2009 - 1990 (m)', zorder=1)
ax.set_title('Thinning glaciers near Longyearbyen')
plt.tight_layout()
plt.show()
# -

# ### Saving the results

ddem.save("temp_ddem.tif")

# ### Rasterize the glacier outlines on the same grid as ddem
# `glacier_mask` is `True` on glaciers, `False` elsewhere.

glacier_mask = outlines_1990.create_mask(ddem)
plt.imshow(glacier_mask.squeeze(), interpolation='none')

# ### Calculate mean dh over glaciers or stable terrain

# Over glaciers:

print(np.mean(ddem.data[glacier_mask]))

# Over stable terrain

print(np.mean(ddem.data[~glacier_mask]))

# Something is wrong, mean dh over stable terrain should be ~0 => we need to coregister the DEMs. 
# This is some proper work for our next example !
