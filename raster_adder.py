import os
import arcpy
from arcpy.sa import *
from arcpy import env

arcpy.CheckOutExtension("Spatial")
env.overwriteOutput = True
__author__ = 'Steve Kochaver'

stdev_path = ""
big_outs_path = ""
template_raster = ""
final_raster_path = ""

env.mask = template_raster
env.extent = template_raster
env.snapRaster = template_raster

final_raster = template_raster


def make_it_big(small_raster):
    '''
    Takes a raster and redefines the extent to the match the template raster defined in our environment variables.
    :param small_raster: The raster with the extent that's smaller than the one you want to add it to.
    :return: Returns the Raster object
    '''
    pmemory = r'in_memory\poly'
    arcpy.CopyRaster_management(small_raster, pmemory)
    big_raster = Raster(pmemory)
    # Gives null value pixels a value of 0 for the purposes of adding to other rasters of the same (new) extent.
    # Saves it in the in-memory raster object and also as a new variable if it needs to be saved somewhere else.
    new_raster = Con(IsNull(big_raster), 0, big_raster)

    return big_raster