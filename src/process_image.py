# -*- coding: utf-8 -*-
"""
Module containing methods to processes a high resolution scanned image.

Created on Tue Apr 25 15:08:53 2017

@author: ukalwa
"""
# Built-in imports
from __future__ import print_function, division
import os
import sys
import posixpath
import time

if sys.version_info[0] < 3:
    import Tkinter as tk
    import ConfigParser as configparser
else:
    import tkinter as tk
    import configparser

# third-party imports
import cv2
import matplotlib.pyplot as plt
from tqdm import tqdm

# Custom module imports
from src.process_block import process_block
from src.utilities import split_image, get_mean
from src.utilities import read_image, get_obj_box
from src.utilities import get_bkground_class
from src.utilities import create_mask

plt.style.use('ggplot')


def process_image(file_path):
    """
    This function reads an high resolution image file, extracts objects and
    gets the total count of them.

    * The image file is of a 3in. diameter Whatman filter paper scanned at \
    4800 dpi using  a flatbed scanner. It consists of nematode eggs and soil \
    debris on it.

    * This function performs these following steps:
        1. It extracts the configuration parameters related to blob \
        identification, figure sizes, bounding box parameters and so on
        2. Read the image file as a 3-d numpy array and splits it into \
        various blocks and stores them as a list of numpy arrays.
        3. It then loops though each block and detects any eggs based on \
        parameters set in the config file and records the count and adds it to\
        the total count
        4. After all the blocks are completed, total egg counts, blocks with\
        bounding boxes around eggs, egg params are all saved in text files\
        for reference and debugging purposes

    :param file_path: absolute file path of the image
    """
    start_time = time.time()
    img = read_image(file_path)
    # Images are split into blocks and saved as list of arrays
    config = configparser.ConfigParser()
    CFG_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                            'config.ini')
    config.read(CFG_PATH)
    # Block params
    block_size = [int(item) for item in config.get(
        'DEFAULT', 'block_size').split(',')]
    mean_thresh = config.getfloat('DEFAULT', 'mean_thresh')

    # Plot params
    dpi = config.getint("fig", "dpi")
    figsize = [int(item) for item in config.get("fig", "size").split(",")]
    ext = config.get("fig", "ext")
    save_fig = config.getboolean("fig", "save")

    # Save options
    save_params = config.getboolean("save", "obj_params")
    save_obj = config.getboolean("save", "obj")
    save_counts = config.getboolean("save", "counts")
    save_bkground = config.getboolean("save", "background")
    box_size = [int(item) for item in config.get("box", "size").split(",")]
    # Added to save binary blocks for machine learning
    save_train = config.getboolean("save", "train")

    total_egg_count = 0  # Total Egg count initialization to 0
    block_count = 0  # To store current block
    count_list = ["Layer, Block, Count"]
    egg_list = ["BLK, A, W, H, W/H"]
    base_file = os.path.splitext(file_path)[0]
    if os.path.sep in base_file:
        file_name = base_file.split(os.path.sep)[-1]
    elif posixpath.sep in base_file:
        file_name = base_file.split(posixpath.sep)[-1]
    else:
        file_name = base_file
    base_mean = get_mean(img, hsv_mean=True)
    obj_list, bkground_list = [], []

    print("Splitting images into image blocks")
    img_list, _ = split_image(img, block_size)
    if base_mean[1] < mean_thresh:
        print("Top or Interface detected")
        layer = "interface"
    else:
        print("Pellet detected")
        layer = "pellet"

    print("Processing all image blocks")
    progress_bar = tqdm(img_list)

    if save_fig:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)

    for block_image in progress_bar:
        progress_bar.set_description("Egg Count: {}".format(total_egg_count))
        b_img = block_image.copy()
        result = process_block(b_img, base_mean,
                               cfg_file=config, blk_cnt=block_count,
                               file_name = file_name)
        count = result['count']
        processed_image = result['img']
        egg_list.extend(result['obj_params'])
        contours = result["contours"]
        mask = result["mask"]

        count_list.append("{}, {}, {}".format(layer, block_count, count))

        # Create binary image from the contours
        if save_train:
            # if len(result["contours"]) > 0:
            binary_image = create_mask(mask.shape, result["contours"])
            save_dir = os.path.join(base_file, "train")
            if not os.path.isdir(save_dir):
                os.makedirs(save_dir)
            # Save mask
            cv2.imwrite(
                    os.path.join(save_dir,
                                "{}_{:04d}_mask{}".format(file_name,
                                block_count, ext)),
                    binary_image)
            # Save original
            cv2.imwrite(
                    os.path.join(save_dir,
                                "{}_{:04d}{}".format(file_name, block_count, ext)),
                    block_image.copy())

        # Save objects
        if save_obj:
            block_img_list, box_lst = get_obj_box(block_image, contours,
                                                  fixed_size=box_size)
            obj_list.extend(block_img_list)

            if save_bkground:
                bkground_list.extend(get_bkground_class(
                    block_image, box_lst, fixed_size=box_size))

        total_egg_count += count
        if save_fig:
            ax1.imshow(cv2.cvtColor(block_image, cv2.COLOR_BGR2RGB))
            ax1.set_title('Original Image')
            # remove xticks and yticks
            ax1.set_yticks([])
            ax1.set_xticks([])

            ax2.imshow(cv2.cvtColor(processed_image, cv2.COLOR_BGR2RGB))
            ax2.set_title('Egg count %s' % count)
            ax2.set_yticks([])
            ax2.set_xticks([])

            if not os.path.isdir(base_file):
                os.mkdir(base_file)
            plt.savefig(posixpath.join(base_file, str(block_count) + ext),
                        bbox_inches='tight', dpi=dpi)
            
        block_count += 1
    plt.close(fig)
    end_time = time.time()
    count_list.append(("Total Eggs counted {} in {} seconds".
                       format(total_egg_count, round(
                               (end_time - start_time), 2))))
    if save_counts:
        with open(posixpath.join(base_file, "count.txt"), "w") as f:
            for s in count_list:
                f.write(str(s) + "\n")
    if save_params:
        with open(posixpath.join(base_file, "egg_list.txt"), "w") as f:
            for s in egg_list:
                f.write(str(s) + "\n")
    if save_obj:
        train_dir = os.path.join(base_file, "train")
        eggs_dir = os.path.join(base_file, "train", "eggs")
        if not os.path.isdir(train_dir):
            os.mkdir(train_dir)
        if not os.path.isdir(eggs_dir):
            os.mkdir(eggs_dir)
        for idx, obj in enumerate(obj_list):
            cv2.imwrite(os.path.join(eggs_dir,
                                     "eggs_{}_{:04d}.jpg".format(
                                         file_name, idx)), obj)
        if save_bkground:
            bkground_dir = os.path.join(base_file, "train", "background")
            if not os.path.isdir(bkground_dir):
                os.mkdir(bkground_dir)
            for idx, obj in enumerate(bkground_list):
                cv2.imwrite(os.path.join(bkground_dir,
                                         "bkg_{}_{:06d}.jpg".format(
                                             file_name, idx)), obj)
    print("Total Eggs counted {} in {} seconds".
          format(total_egg_count, round((end_time - start_time), 2)))
