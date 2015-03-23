import ogr
import gdal
from gdalconst import *
import os

gdal.UseExceptions()
__author__ = 'Steve Kochaver'

def template_raster(base_raster_path, out_raster, data_type=gdal.GDT_Int32, no_data=-1):
    '''
    This function is meant to create an empty template raster from an existing raster. By empty I mean "filled with
    zero value pixels". Imagine that you are an artist. The raster template is now your canvas, since it is difficult to
    create a canvas from scratch...you would need your own raw cotton, gesso, pixel sizes, geotransforms, etc.
    :param base_raster_path: This is the path to the raster from which you will create the template.
    :param out_raster: This is the path to the output template raster file.
    :param data_type: This is the type of data each pixel in the raster holds. 32 bit integer is the default.
    :param no_data: This is not implemented right now. There is a line if you want to define your own NoData values in the raster
    :return: Return the template Raster object. It also exists at your path.
    '''


    base_raster = gdal.Open(base_raster_path)

    cols = base_raster.RasterXSize
    rows = base_raster.RasterYSize
    projection = base_raster.GetProjection()
    geotransform = base_raster.GetGeoTransform()
    # bands = base_raster.RasterCount
    bands = 1

    driver = gdal.GetDriverByName("GTIFF")
    new_raster = driver.Create(out_raster, cols, rows, bands, data_type)
    new_raster.SetProjection(projection)
    new_raster.SetGeoTransform(geotransform)

    for i in range(bands):
        new_raster.GetRasterBand(i + 1).SetNoDataValue(None)  # Change these zeros if there is important data in base data or params
        # new_raster.GetRasterBand(i + 1).SetNoDataValue(no_data)  # If you want to implement a no data value uncomment this line
        new_raster.GetRasterBand(i + 1).Fill(0)   # Change these zeros if there is important data in base data or params

    return new_raster

def add_to_raster(base_raster, shape_file):
    '''
    Takes a shape file and burns the values into the raster with a value of 1. That is to say if the shape feature
    touches a pixel in the base raster the value of that pixel will be increased by 1. Values will be added.
    :param base_raster: The path to the raster to which you will be adding burned values.
    :param shape_file: The path to the .shp shape file with your feature geometry.
    :return: Doesn't return anything. Sorry if that's disappointing.
    '''

    vector = ogr.Open(shape_file)
    layer = vector.GetLayer()
    add_out = gdal.Open(base_raster, GA_Update)

    # This next line is the bread and butter. Variables in order are: the base raster opened by GDAL for editing, the band
    # in the raster for editing, the shapefile layer we will burn, the value of the burn (just 1 here for True), and the
    # crazy GDAL options: ALL_TOUCHED means each pixel "touched" by the layer rather than completely within, and MERGE_ALGORITHM
    # ADD meaning burn values will be added to the existing pixel values.

    gdal.RasterizeLayer(add_out, [1], layer, burn_values=[1], options=['ALL_TOUCHED=TRUE', 'MERGE_ALG=ADD'])

    # Clears the references because spooky stuff has a tendency to happen otherwise. Like the GIS X Files.
    vector = None
    add_out = None

    return

def create_out_tiff(in_file, out_file, initial_shp):
    '''
    This function is another attempt at creating a template raster file from an existing raster to define the raster
    properties and a shape file to define the extent. I recommend using template_raster if you can.
    :param in_file: The path to the input raster dataset.
    :param out_file: The path to put the new raster template dataset.
    :param initial_shp: The shape file that will define the initial extent of the raster.
    :return: Doesn't return anything. Just makes your file or it gets the hose again.
    '''

    in_source = gdal.Open(in_file)
    out_source = gdal.GetDriverByName("GTiff").Create(out_file, in_source.RasterXSize, in_source.RasterYSize, 1, gdal.GDT_Int32)

    out_source.SetProjection(in_source.GetProjection())
    out_source.SetGeoTransform(in_source.GetGeoTransform())

    vector_source = ogr.Open(initial_shp)
    layer = vector_source.GetLayer()

    gdal.RasterizeLayer(out_source, [1], layer, burn_values=[0], options=['ALL_TOUCHED=TRUE'])

    in_source = None
    out_source = None
    vector_source = None
    return

def burn_without_add(in_raster, in_shape):
        '''
        Burn the values of a shapefile into a base raster. Replaces the values of the pixel in the raster rather then
        adding to them.
        :param in_raster: The path to the input raster.
        :param in_shape: The path to the shapefile with the geometries you care about.
        :return: Doesn't return anything.
        '''
        shape_source = ogr.Open(in_shape)
        layer = shape_source.GetLayer()

        raster_source = gdal.Open(in_raster, GA_Update)

        gdal.RasterizeLayer(raster_source, [1], layer, burn_values=[1], options=['ALL_TOUCHED=TRUE'])

        shape_source = None
        raster_source = None
        return