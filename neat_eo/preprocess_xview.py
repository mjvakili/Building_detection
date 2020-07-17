import numpy as np
import os
import sys
import shutil
import argparse

from pathlib import Path
import json

import pandas as pd
import shapely.wkt
from rasterio.features import rasterize
from PIL import Image
import logging
from collections import defaultdict

from core import load_config, make_palette

logger = logging.getLogger(__name__)
logging.getLogger("fiona").setLevel(logging.ERROR)
logging.getLogger("fiona.collection").setLevel(logging.ERROR)
logging.getLogger("rasterio").setLevel(logging.ERROR)
logging.getLogger("PIL.PngImagePlugin").setLevel(logging.ERROR)


def exception_logger(exception_type, exception_value, exception_traceback):
    logger.error(
        "Uncaught Exception",
        exc_info=(exception_type, exception_value, exception_traceback),
    )


sys.excepthook = exception_logger


def get_disaster_dict(generator):
    """
    Groups images and labels by disaster
    """
    disaster_dict = defaultdict(list)
    for file in generator:
        disaster_type = file.name.split('_')[0]
        disaster_dict[disaster_type].append(str(file))
    return disaster_dict


def crop(img, height, width, image_height, image_width):
    for i in range(int(image_height // height)):
        for j in range(int(image_width // width)):
            box = (j * width, i * height, (j + 1) * width, (i + 1) * height)
            yield img.crop(box)


def crop_image(image, crop_res):
    """
    Splits image into pieces with specified resolution
    :param image: PIL.Image to be split
    :param crop_res: tuple with width and height of separate pieces of image
    """

    image_width, image_height = image.size
    width, height = crop_res

    pieces = []
    for piece in crop(image, height, width, image_width, image_height):
        pieces.append(piece)

    return pieces


def rasterizing(json_file, crop_res, dest, config):
    """
    Create label masks
    """

    palette, transparency = make_palette([classe["color"] for classe in config["classes"]], complementary=True)

    # read label file
    with open(json_file, 'r') as f:
        data = json.load(f)

    # Load in building coordinates
    label_info = pd.json_normalize(data['features'], 'xy')

    # Buildings on image
    if not label_info.empty:
        # Empty raster to be filled
        result = np.zeros([1024, 1024])  # Width and height of original image

        # Create label mask
        for index, row in label_info.iterrows():
            building = shapely.wkt.loads(row['wkt'])
            coords = list(zip(building.exterior.coords.xy[0], building.exterior.coords.xy[1]))
            geom = {'type': building.geom_type, 'coordinates': [coords]}
            raster = rasterize([geom], out_shape=[1024, 1024])
            result = np.logical_or(result, raster)

        out = Image.fromarray(result, mode="P")
        out.putpalette(palette)

    # No buildings on image
    else:
        out = Image.new('P', (1024, 1024))
        out.putpalette(palette)

    # Check if image needs to be cropped
    if crop_res:

        pieces = crop_image(out, crop_res)

        # save separate pieces of image
        for k, piece in enumerate(pieces):

            path = dest[:-4] + str(k + 1) + '.png'

            if transparency is not None:
                piece.save(path, optimize=True, transparency=transparency)
            else:
                piece.save(path, optimize=True)
    else:
        if transparency is not None:
            out.save(dest, optimize=True, transparency=transparency)
        else:
            out.save(dest, optimize=True)

    return


def create_datapoints(config, crop_res):
    """
    The dataloader as defined by Neat-EO requires the following directory structure '[0-9]*/[0-9]*/[0-9]*'
    to load in images and labels. Therefore, integers from 0 to #disasters-1 are used as directory names.
    A text file will be created to figure out which directory belongs to which disaster.

    :param crop_res: None or tuple with width and height of images into which original image should be split

    Adjust dataloader?
    """

    root = "../data/xview/"

    # Fetch all pre disaster json files
    labels_pre = Path(root + 'labels').rglob(pattern=f'*pre_*.json')

    # Fetch all pre disaster images
    images_pre = Path(root + 'images').rglob(pattern=f'*pre_*.png')

    # Labels and images dicts
    labels_per_disaster = get_disaster_dict(labels_pre)
    images_per_disaster = get_disaster_dict(images_pre)

    # Translation key for directories to disasters
    disaster_key = defaultdict(list)

    for idx, disaster in enumerate(labels_per_disaster.keys()):

        logger.info("Creating label masks for {}".format(disaster))

        # Save index to disaster translation
        disaster_key[idx] = disaster

        # Images and labels for this disaster
        labels = labels_per_disaster[disaster]
        images = images_per_disaster[disaster]

        # Make sure label corresponds to image on same index
        labels.sort()
        images.sort()

        # Split datapoints
        all_indexes = list(range(len(labels)))

        np.random.shuffle(all_indexes)

        training_offset = int(len(all_indexes) * 0.8)

        validation_offset = int(len(all_indexes) * 0.9)

        split_mappings = {
            "train": all_indexes[:training_offset],
            "validation": all_indexes[training_offset:validation_offset],
            "test": all_indexes[validation_offset:]
        }

        for split in split_mappings:
            # create labels directory for split
            label_directory = os.path.join(root, split, 'labels/1', str(idx))
            if not os.path.exists(label_directory):
                os.makedirs(label_directory, exist_ok=True)

            # create image directory for split
            image_directory = os.path.join(root, split, 'images/1', str(idx))
            if not os.path.exists(image_directory):
                os.makedirs(image_directory, exist_ok=True)

            # save image and label
            for index in split_mappings[split]:

                # check if image needs to be cropped
                if crop_res:
                    image = Image.open(images[index])
                    pieces = crop_image(image, crop_res)

                    # save separate pieces of image
                    for k, piece in enumerate(pieces):
                        path = os.path.join(image_directory, images[index].split('_')[1] + str(k + 1) + '.png')
                        piece.save(path)
                # if no cropping is needed, simply copy file to right directory
                else:
                    shutil.copyfile(images[index], os.path.join(image_directory, images[index].split('_')[1] + '.png'))

                # Create and save label mask
                rasterizing(labels[index], crop_res,
                            os.path.join(label_directory, labels[index].split('_')[1] + '.png'), config)

    # Write disaster translation away
    with open(root + 'key.txt', 'w') as file:
        file.write(json.dumps(disaster_key))

    return


def main():
    logging.basicConfig(
        handlers=[
            logging.FileHandler(os.path.join(".", "run.log")),
            logging.StreamHandler(sys.stdout),
        ],
        level=logging.DEBUG,
        format="%(asctime)s %(name)s %(levelname)s %(message)s",
    )

    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument(
        "--config",
        type=str,
        default=None,
        help="Path to config file",
    )

    parser.add_argument(
        "--crop",
        type=int,
        nargs="+",
        default=None,
        help="Width (int) and height (int) of pieces image needs to be cropped to",
    )

    args = parser.parse_args()

    # read config
    logger.info("Reading config file: {}".format(args.config))
    config = load_config(args.config)

    # start processing
    logger.info("Start creating datapoints")
    create_datapoints(config, args.crop)


if __name__ == "__main__":
    main()
