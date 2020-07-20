import os
import sys
import numpy as np
import re
import glob
import argparse
import logging
from PIL import Image
from matplotlib import cm
import matplotlib.pyplot as plt

try:
    from itertools import ifilterfalse
except ImportError:  # py3k
    from itertools import filterfalse

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


def mean(l, ignore_nan=False, empty=0):
    """
    nanmean compatible with generators.
    """
    l = iter(l)
    if ignore_nan:
        l = ifilterfalse(np.isnan, l)
    try:
        n = 1
        acc = next(l)
    except StopIteration:
        if empty == 'raise':
            raise ValueError('Empty mean')
        return empty
    for n, v in enumerate(l, 2):
        acc += v
    if n == 1:
        return acc
    return acc / n


def atoi(text):
    return int(text) if text.isdigit() else text


def natural_keys(text):
    """
    alist.sort(key=natural_keys) sorts in human order
    http://nedbatchelder.com/blog/200712/human_sorting.html
    (See Toothy's implementation in the comments)
    """
    return [atoi(c) for c in re.split(r'(\d+)', text)]


def iou_binary(masks, labels, EMPTY=1., ignore=None, per_image=True):
    """
    IoU for foreground class
    binary: 1 foreground, 0 background
    """
    if not per_image:
        masks, labels = (masks,), (labels,)
    ious = []
    for mask, label in zip(masks, labels):
        intersection = ((label == 1) & (mask == 1)).sum()
        union = ((label == 1) | ((mask == 1) & (label != ignore))).sum()
        if not union:
            iou = EMPTY
        else:
            iou = float(intersection) / union
        ious.append(iou)
    iou = mean(ious)  # mean accross images if per_image
    return iou


def eval_map(preds, labels, path):
    """
    Creates difference and colors maps of labels and masks

    STILL BUGGY, NEED FIXING!
    """
    num = 1
    for pred, label in zip(preds, labels):
        # tn = np.logical_and(pred==0,label==0).astype(int)
        fp = np.logical_and(pred == 1, label == 0).astype(int)
        fn = np.logical_and(pred == 0, label == 1).astype(int)
        tp = np.logical_and(pred == 1, label == 1).astype(int)

        diff = fp + fn
        color = fp + (2 * fn) + (3 * tp)

        diff_map_path = os.path.join(path, "diff_maps")
        os.makedirs(diff_map_path, exist_ok=True)
        plt.imsave(os.path.join(diff_map_path, str(num), ".png"), diff, cmap=cm.Greys)

        color_map_path = os.path.join(path, "color_maps")
        os.makedirs(color_map_path, exist_ok=True)
        plt.imsave(os.path.join(color_map_path, str(num), ".png"), color, cmap=cm.Greys)

        num += 1

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
        "--dataset",
        type=str,
        default=None,
        help="Path to directory in which labels and masks are stored"
    )

    parser.add_argument(
        "--eval_maps",
        type=bool,
        default=False,
        help="create evaluation maps"
    )

    args = parser.parse_args()

    logger.info("Calculating IoU")

    # Load labels
    label_paths = glob.glob(os.path.join(args.dataset, "labels", "[0-9]*/[0-9]*/[0-9]*.*"))
    label_paths.sort(key=natural_keys)
    labels = [np.asarray(Image.open(label), dtype='int32') for label in label_paths]

    # Load masks
    mask_paths = glob.glob(os.path.join(args.dataset, "masks", "[0-9]*/[0-9]*/[0-9]*.*"))
    mask_paths.sort(key=natural_keys)
    masks = [np.asarray(Image.open(mask), dtype='int32') for mask in mask_paths]

    iou = iou_binary(labels, masks)
    logger.info("Mean Iou: {}".format(iou))

    if args.eval_maps:
        logger.info("Creating evaluation maps")
        eval_map(labels, masks, args.dataset)


if __name__ == "__main__":
    main()
