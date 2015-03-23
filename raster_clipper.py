import os
import arcpy
from arcpy.sa import *

__author__ = 'Steve Kochaver'
arcpy.CheckOutExtension('Spatial')


def get_band_list(raster):
    """
    Returns a list of all the band names in a raster.
    :param raster: The path to the raster dataset.
    :return: List of band names as strings.
    """
    
    describe = arcpy.Describe(raster)  # Arc Description object of raster
    band_list = [band.name for band in describe.children]
    
    return band_list

def bands_to_raster_obj(raster, band_list):
    '''
    Saves a list of Raster objects to memory. One for each band given for a raster dataset.
    :param raster: The path of the raster dataset holding the band_list bands.
    :param band_list: List of all the band names within the raster dataset.
    :return: List object of full band paths.
    '''

    raster_list = [Raster(os.path.join(raster, band)) for band in band_list]

    return raster_list

def custom_nodata(rlist):
    '''
    Mask creation specific to Ryan Sword's aviris .bsq data. Takes the list of bands Plus1.96, PlusStDev, Mean,
    MinusStDev, and Minus1.96 and uses the specific signature of no data values (0 for all bands and the values listed
    below) to create a mask of the meaningful part of the image.
    :param rlist:
    :return: Returns raster object in memory
    '''
    val_1 = 2.1812543869018555  # Plus 1.96
    val_2 = 1.8875709772109985  # Plus StDev
    val_3 = 1.581650972366333   # Mean
    val_4 = 1.2757309675216675  # Minus StDev
    val_5 = 0.9820476770401001  # Minus 1.96

    # Conditional sets new raster values to zero if all band values are also zero
    new_raster = Con(((rlist[0] == 0) & (rlist[1] == 0) & (rlist[2] == 0) & (rlist[3] == 0) & (rlist[4] == 0)), 0, 1)

    # Conditional sets new raster values to zero if equal to above values and not within previous conditional scope
    new_raster = Con(new_raster == 1, Con(((rlist[0] == val_1) & (rlist[1] == val_2) & (rlist[2] == val_3) & (rlist[3] == val_4) & (rlist[4] == val_5)), 0, 1), new_raster)

    # Set zero to null in new raster. Only have data where there is meaningful data in original.
    new_raster = SetNull(new_raster == 0, new_raster)

    return new_raster


def raster_to_polygon(raster_path, output_path):
    '''
    Creates a polygon footprint of a binary (1 or 0) raster.
    :param raster_path: The path to the raster you want to turn into a polygon
    :param output_path: The path to where you want the output to go.
    :return:
    '''
    raster = Raster(raster_path)
    mask_raster = Con((raster == 0) | (raster == 1), 1, 0)
    arcpy.RasterToPolygon_conversion(mask_raster, output_path, "NO_SIMPLIFY")
    return
