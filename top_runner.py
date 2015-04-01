from raster_clipper import *
from stdev_rangefinder import get_date, check_stdev_range, check_196stdev_range
from raster_adder import add_small_rasters
import arcpy
from rasterizer import add_to_raster
from arcpy.sa import *
import tempfile
import shutil
import os

__author__ = 'Steve Kochaver'


def listdir_fullpath(directory):
    return [os.path.join(directory, name) for name in os.listdir(directory)]


def get_files_of_ext(directory, extension):
    return [path for path in listdir_fullpath(directory) if os.path.splitext(path)[1].lower() == extension]


def create_path_footprints(image_directory, burn_raster_path):
    '''
    Given a directory containing .bsq images and a path to an 0 constant raster this function will add 1 to every raster
    pixel where there is meaningful data in the raster. Converts to shapefile in directory and burns based on the
    output polygon geometry. Puts those shapefiles into a temporary directory then removes the directory.
    :param image_directory: The directory containing the raster images
    :param burn_raster_path: The path to the 0 constant raster. Should be of an extent that contains all the paths.
    :return:
    '''
    temp_dir = tempfile.mkdtemp()

    for image in get_files_of_ext(image_directory, '.tif'):

        image_name = os.path.splitext(os.path.basename(image))[0]
        # con_raster = custom_nodata(bands_to_raster_obj(image, get_band_list(image))) for bsq images
        raster = Raster(image)
        mask_raster = Con((raster == 0) | (raster == 1), 1, 0)
        output_path = os.path.join(temp_dir, image_name + '.shp')
        arcpy.RasterToPolygon_conversion(mask_raster, output_path, "NO_SIMPLIFY")

        add_to_raster(burn_raster_path, output_path)

    shutil.rmtree(temp_dir)

    return


def stdev_analysis(image_directory, template_raster_path, int_count_raster):
    '''
    Does the standard deviation analysis for the .bsq images in the given image directory. Creates a directory of
    all the analysis outputs in said directory then creates a count raster of all those outputs.
    :param image_directory: The directory of the images (N, LIG, or LMA) for analysis.
    :param template_raster_path: The zero constant raster of the maximum extent of all the paths.
    :return:
    '''

    stdev_dir = os.path.join(image_directory, 'stdev_outs')
    if not os.path.exists(stdev_dir): os.makedirs(stdev_dir)

    meaningful_files = get_files_of_ext(image_directory, '.bsq')
    remaining_files = meaningful_files[:]

    for raster_file in meaningful_files:
        print raster_file
        remaining_files.remove(raster_file)
        for compare_file in remaining_files:
            print '\t' + compare_file
            output_path = os.path.join(os.getcwd(), stdev_dir, get_date(raster_file) + '_TO_' + get_date(compare_file) + '.tif')
            try:
                check_stdev_range(raster_file, compare_file, output_path)
            except:
                pass

    true_count_path = os.path.join(stdev_dir, 'stdev_true_count.tif')
    add_small_rasters(stdev_dir, template_raster_path, true_count_path)

    per_raster_path = os.path.join(stdev_dir, 'stdev_percent.tif')
    per_calc = Raster(true_count_path) * 1.0 / Raster(int_count_raster) * 1.0
    per_calc.save(per_raster_path)
    return

def _196stdev_analysis(image_directory, template_raster_path, int_count_raster):
    '''
    Does the standard deviation analysis for the .bsq images in the given image directory. Creates a directory of
    all the analysis outputs in said directory then creates a count raster of all those outputs.
    :param image_directory: The directory of the images (N, LIG, or LMA) for analysis.
    :param template_raster_path: The zero constant raster of the maximum extent of all the paths.
    :return:
    '''

    stdev_dir = os.path.join(image_directory, '196stdev_outs')
    if not os.path.exists(stdev_dir): os.makedirs(stdev_dir)

    meaningful_files = get_files_of_ext(image_directory, '.bsq')
    remaining_files = meaningful_files[:]

    for raster_file in meaningful_files:
        print raster_file
        remaining_files.remove(raster_file)
        for compare_file in remaining_files:
            print '\t' + compare_file
            output_path = os.path.join(os.getcwd(), stdev_dir, get_date(raster_file) + '_TO_' + get_date(compare_file) + '.tif')
            try:
                check_196stdev_range(raster_file, compare_file, output_path)
            except:
                pass

    true_count_path = os.path.join(stdev_dir, '196stdev_true_count.tif')
    add_small_rasters(stdev_dir, template_raster_path, true_count_path)

    per_raster_path = os.path.join(stdev_dir, '196stdev_percent.tif')
    per_calc = Raster(true_count_path) * 1.0 / Raster(int_count_raster) * 1.0
    per_calc.save(per_raster_path)
    return

n_path = r"C:\_sword_analysis\3-27-15\N"
intersection_count_raster = r"C:\_sword_analysis\3-27-15\path_intersection_count.tif"
template_raster_path = r"C:\_sword_analysis\3-27-15\empty_raster.tif"

_196stdev_analysis(n_path, template_raster_path, intersection_count_raster)
