import os
import arcpy
from arcpy.sa import *
from arcpy import env
import tempfile
import shutil

arcpy.CheckOutExtension("Spatial")
env.overwriteOutput = True
__author__ = 'Steve Kochaver'


def listdir_fullpath(directory):
    return [os.path.join(directory, name) for name in os.listdir(directory)]


def get_files_of_ext(directory, extension):
    return [path for path in listdir_fullpath(directory) if os.path.splitext(path)[1].lower() == extension]

def make_it_big(small_raster_path, big_raster_path):
    '''
    Takes a raster and redefines the extent to the match the template raster defined in our environment variables.
    :param small_raster: The raster with the extent that's smaller than the one you want to add it to.
    :return: Returns the Raster object
    '''
    name, ext = os.path.splitext(big_raster_path)
    temp_raster = name + '-temp' + ext

    arcpy.CopyRaster_management(small_raster_path, temp_raster)
    big_raster =Raster(temp_raster)
    # Gives null value pixels a value of 0 for the purposes of adding to other rasters of the same (new) extent.
    # Saves it in the in-memory raster object and also as a new variable if it needs to be saved somewhere else.
    new_raster = Con(IsNull(temp_raster), 0, temp_raster)
    new_raster.save(big_raster_path)
    arcpy.Delete_management(temp_raster)

    return


def add_small_rasters(small_directory, template_raster_path, final_raster_path):

    env.mask = template_raster_path
    env.extent = template_raster_path
    env.snapRaster = template_raster_path

    template_raster = Raster(template_raster_path)

    temp_dir = tempfile.mkdtemp()

    for image in get_files_of_ext(small_directory, '.tif'):
        image_name = os.path.splitext(os.path.basename(image))[0]
        big_path = os.path.join(temp_dir, image_name+'.tif')

        make_it_big(image, big_path)
        template_raster = template_raster + big_path

    template_raster.save(final_raster_path)
    shutil.rmtree(temp_dir)
    return

