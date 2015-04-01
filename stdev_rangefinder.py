import os
import arcpy
from arcpy import env
from arcpy.sa import *
import raster_clipper
import ntpath

print 'Packages Loaded'
env.overwriteOutput = True
__author__ = 'Steve Kochaver'

def remove_nodata(in_raster_path):
    '''
    Sets logical NoData values to Null in a 5 band raster. Assumes that the NoData values are those values where
    the pixel in every band is equal to 0.
    :param in_raster_path: The path to the five band raster in question.
    :return: Returns and Arc Raster object with the new Null pixels.
    '''

    band_list = raster_clipper.get_band_list(in_raster_path)
    rlist = raster_clipper.bands_to_raster_obj(in_raster_path, band_list)
    in_raster = Raster(in_raster_path)

    #  Conditional statement finding pixels where all bands are 0 and sets to Null.
    new_raster = SetNull(((rlist[0] == 0) & (rlist[1] == 0) & (rlist[2] == 0) & (rlist[3] == 0) & (rlist[4] == 0)), in_raster)

    return new_raster

def raster_intersection(raster_1_path, raster_2_path):
    '''
    Given two rasters this function will find data-full intersection between them and create an unsimplified polygon (i.e. the
    polygon will follow the exact edges of the pixels) of that intersection.
    :param raster_1_path: The path to one of the raster datasets.
    :param raster_2_path: The path to the other raster.
    :return: Returns and Arc polygon object as well as the path (in memory) to the shapefile containing that polygon.
    '''
    raster_1 = remove_nodata(raster_1_path)
    raster_2 = remove_nodata(raster_2_path)

    rintersection = Con((raster_1 == True) & (raster_2 == True), 1, 0)

    pmemory = 'in_memory//poly'
    ext_poly = arcpy.RasterToPolygon_conversion(rintersection, pmemory, "NO_SIMPLIFY")

    return ext_poly, pmemory

def check_stdev_range(raster_1_path, raster_2_path, con_raster_path):
    '''
    A custom conditional function that creates a binary raster from two five band rasters. Assumes the third band is
    the mean of the data, and the 2nd and 4th bands are the maximum and minimum of a single standard deviation respectively.
    If the mean of raster 1 falls within the range of raster 2 a value of 1 (True) is given to the output raster. Otherwise
    0 (False).
    :param raster_1_path: The path to raster 1 (mean raster)
    :param raster_2_path: The path to raster 2 (range raster)
    :param con_raster_path: The location of the final conditional output.
    :return:
    '''
    bound_poly, pmemory = raster_intersection(raster_1_path, raster_2_path)

    band_list_1 = raster_clipper.get_band_list(raster_1_path)
    rlist1 = raster_clipper.bands_to_raster_obj(raster_1_path, band_list_1)

    band_list_2 = raster_clipper.get_band_list(raster_2_path)
    rlist2 = raster_clipper.bands_to_raster_obj(raster_2_path, band_list_2)

    in_range_raster = Con((rlist1[2] >= rlist2[3]) & (rlist1[2] <= rlist2[1]), 1, 0)
    arcpy.Clip_management(in_range_raster, '#', con_raster_path, bound_poly, '255', "ClippingGeometry")

    arcpy.Delete_management(pmemory)
    return

def check_196stdev_range(raster_1_path, raster_2_path, con_raster_path):
    '''
    Does the same thing as the check_stdev_range function with the same assumptions using band 1 and 5 as the range.
    :param raster_1_path: The path to raster 1 (mean raster)
    :param raster_2_path: The path to raster 2 (range raster)
    :param con_raster_path: The location of the final conditional output
    :return:
    '''

    bound_poly, pmemory = raster_intersection(raster_1_path, raster_2_path)

    band_list_1 = raster_clipper.get_band_list(raster_1_path)
    rlist1 = raster_clipper.bands_to_raster_obj(raster_1_path, band_list_1)

    band_list_2 = raster_clipper.get_band_list(raster_2_path)
    rlist2 = raster_clipper.bands_to_raster_obj(raster_2_path, band_list_2)

    in_range_raster = Con((rlist1[2] >= rlist2[4]) & (rlist1[2] <= rlist2[0]), 1, 0)
    arcpy.Clip_management(in_range_raster, '#', con_raster_path, bound_poly, '255', "ClippingGeometry")

    arcpy.Delete_management(pmemory)
    return

def create_const_raster(base_raster_path, constant):
    '''
    Given a raster dataset and any integer number this function will create a constant raster at the same extent as
    the input raster.
    :param base_raster_path: The path to the raster we'll use as a template.
    :param constant: The integer value to use in the constant.
    :return:
    '''

    base_raster = Raster(base_raster_path)

    data_type = "INTEGER"
    cell_size = arcpy.GetRasterProperties_management(base_raster, "CELLSIZEX")
    x_min = arcpy.GetRasterProperties_management(base_raster, "LEFT")
    x_max = arcpy.GetRasterProperties_management(base_raster, "RIGHT")
    y_min = arcpy.GetRasterProperties_management(base_raster, "BOTTOM")
    y_max = arcpy.GetRasterProperties_management(base_raster, "TOP")
    extent = Extent(x_min, y_min, x_max, y_max)
    constant_raster = CreateConstantRaster(constant, data_type, cell_size, extent)

    return constant_raster


def get_date(file_path):
    '''
    Takes the file names specific to these five band rasters and slices strings until you have a unique date identifier.
    :param file_path: The full path to the file we need the date from
    :return: The date string we cut from the file path
    '''
    name = ntpath.basename(file_path)
    date = name[1:7]
    full_date = date + '_' + name[14:16]
    return full_date


def run_stdev_finder():
    '''
    !!!No longer relevant but I'll keep it here for nostalgia's sake!!!
    This is a runner function that goes through each .bsq five band file and creates comparison files for each other
    .bsq five band file of a later date. Puts the conditional comparisons into a folder in the current working directory
    called "stdev_outs".
    :return:
    '''
    meaningful_files = [thing for thing in os.listdir(os.getcwd()) if '.bsq' in thing]
    remaining_files = meaningful_files[:]

    for raster_file in meaningful_files:
        print raster_file
        remaining_files.remove(raster_file)
        for compare_file in remaining_files:
            print '\t' + compare_file
            output_path = os.path.join(os.getcwd(), "stdev_outs//", get_date(raster_file) + '_TO_' + get_date(compare_file) + '.tif')
            try:
                check_stdev_range(raster_file, compare_file, output_path)
            except:
                pass
    return


def run_196stdev_finder():
    '''
    !!!No longer relevant but I'll keep it here for nostalgia's sake!!!
    Runs the 1.96 standard deviation finder in the same manner as the run_stdev_finder function.
    :return:
    '''
    meaningful_files = [thing for thing in os.listdir(os.getcwd()) if '.bsq' in thing]
    remaining_files = meaningful_files[:]

    for raster_file in meaningful_files:
        print raster_file
        remaining_files.remove(raster_file)
        for compare_file in remaining_files:
            print '\t' + compare_file
            output_path = os.path.join(os.getcwd(), "196stdev_outs//", get_date(raster_file) + '_TO_' + get_date(compare_file) + '.tif')

            try:
                check_196stdev_range(raster_file, compare_file, output_path)
            except RuntimeError:
                pass

    return