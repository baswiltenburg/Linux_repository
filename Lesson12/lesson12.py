# import modules
from osgeo import gdal
from osgeo.gdalconst import GA_ReadOnly, GDT_Float32
import numpy as np
import subprocess
import os

# open file and print info about the file
# the "../" refers to the parent directory of my working directory
os.chdir('/home/ubuntu/Python')
band5 = gdal.Open('../Python/Lesson12/data/LC81980242014260LGN00_sr_band5.tif', GA_ReadOnly)
band3 = gdal.Open('../Python/Lesson12/data/LC81980242014260LGN00_sr_band3.tif', GA_ReadOnly)

                                    
print "\nInformation about " + '../Python/Lesson12/data/LC81980242014260LGN00_sr_band3.tif'
print "Driver: ", band3.GetDriver().ShortName,"/", \
      band3.GetDriver().LongName
print "Size is ",band3.RasterXSize,"x",band3.RasterYSize, \
      'x',band3.RasterCount

print '\nProjection is: ', band3.GetProjection()

print "\nInformation about the location of the image and the pixel size:"
geotransform = band3.GetGeoTransform()
if not geotransform is None:
    print 'Origin = (',geotransform[0], ',',geotransform[3],')'
    print 'Pixel Size = (',geotransform[1], ',',geotransform[5],')'
 
  
band3Arr = band3.GetRasterBand(1).ReadAsArray(0,0,band3.RasterXSize, band3.RasterYSize)
band5Arr = band5.GetRasterBand(1).ReadAsArray(0,0,band5.RasterXSize, band5.RasterYSize)
                            

# set the data type
band3Arr=band3Arr.astype(np.float32)
band5Arr=band5Arr.astype(np.float32)

# Derive the ndwi
mask = np.greater(band3Arr+band5Arr,0)

# set np.errstate to avoid warning of invalid values (i.e. NaN values) in the divide 
with np.errstate(invalid='ignore'):
    ndwi = np.choose(mask,(-99,(band3Arr-band5Arr)/(band3Arr+band5Arr)))
print "WDVI min and max values", ndwi.min(), ndwi.max()
# Check the real minimum value
print ndwi[ndwi>-99].min()

# Write the result to disk
driver = gdal.GetDriverByName('GTiff')
outDataSet=driver.Create('../Python/Lesson12/ndwi.tif', band5.RasterXSize, band5.RasterYSize, 1, GDT_Float32)
outBand = outDataSet.GetRasterBand(1)
outBand.WriteArray(ndwi,0,0)
outBand.SetNoDataValue(-99)

# set the projection and extent information of the dataset
outDataSet.SetProjection(band3.GetProjection())
outDataSet.SetGeoTransform(band5.GetGeoTransform())


# Finally let's save it... or like in the OGR example flush it
outBand.FlushCache()
outDataSet.FlushCache()

# reproject the .tif file. 
subprocess.call(["gdalinfo", "../Python/Lesson12/ndwi.tif"])
subprocess.call(["gdalwarp", "-t_srs", "EPSG:4326", "../Python/Lesson12/ndwi.tif", "../Python/Lesson12/ndwi_reproject.tif"])

# Let's check what the result is
subprocess.call(["gdalinfo", "../Python/Lesson12/ndwi_reproject.tif"])


# Notebook magic to select the plotting method
# Change to inline to plot within this notebook
from osgeo import gdal
import matplotlib.pyplot as plt

# Open image
dsll = gdal.Open("../Python/Lesson12/ndwi_reproject.tif")

# Read raster data
ndwi_img = dsll.ReadAsArray(0, 0, dsll.RasterXSize, dsll.RasterYSize)

# Now plot the raster data using gist_earth palette

plt.imshow(ndwi_img, interpolation='nearest', vmin=0, clim=(-1, 2))
plt.show()

dsll = None


subprocess.call(["gdalinfo", "../Python/Lesson12/ndwi.tif"])
subprocess.call(["gdalwarp", "-t_srs", "EPSG:4326", "../Python/Lesson12/ndwi.tif", "../Python/Lesson12/ndwi_reproject.tif"])

# Check what the result is
subprocess.call(["gdalinfo", "../Python/Lesson12/ndwi_reproject.tif"])
