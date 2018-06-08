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
import cv2  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from tqdm import tqdm  # noqa: E402

# Custom module imports
from src.process_block import process_block  # noqa: E402
from src.utilities import split_image, get_mean  # noqa: E402
from src.utilities import validate_file, read_image  # noqa: E402

plt.style.use('ggplot')


def process_image(file_path, obj=None, save_obj=False):
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
    :param obj: storing obj params for debugging purposes
    :param save_obj: save these obj params to a file for viewing them later
    """
    start_time = time.time()
    img = read_image(file_path)
    if not obj:
        obj = {"sizes": [], "detected": [], "mean": []}
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
    create_plots = config.getboolean("fig", "create")
    save_images = config.getboolean("fig", "save")
    show_plots = config.getboolean("fig", "show")
    if not show_plots:
        plt.ioff()

    total_egg_count = 0  # Total Egg count initialization to 0
    block_count = 0  # To store current block
    count_list = ["Layer, Block, Count"]
    egg_list = ["BLK, A, W, H, W/H"]
    base_file = os.path.splitext(file_path)[0]
    base_mean = get_mean(img, hsv_mean=True)

    print("Splitting images into image blocks")
    img_list = split_image(img, block_size)
    if base_mean[1] < mean_thresh:
        print("Top or Interface detected")
        layer = "interface"
    else:
        print("Pellet detected")
        layer = "pellet"

    print("Processing all image blocks")
    progress_bar = tqdm(img_list)
    for block_image in progress_bar:
        progress_bar.set_description("Egg Count: {}".format(total_egg_count))
        b_img = block_image.copy()
        result = process_block(b_img, base_mean,
                               retr_objects=save_obj,
                               cfg_file=config, blk_cnt=block_count)
        count = result['count']
        processed_image = result['img']
        egg_list.extend(result['obj_params'])

        for key in obj:
            obj[key].extend(result["obj"][key])

        count_list.append("{}, {}, {}".format(layer, block_count, count))
        total_egg_count += count
        if create_plots:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)
            ax1.imshow(cv2.cvtColor(block_image, cv2.COLOR_BGR2RGB))
            ax1.set_title('Original Image')
            # remove xticks and yticks
            ax1.set_yticks([])
            ax1.set_xticks([])

            ax2.imshow(cv2.cvtColor(processed_image, cv2.COLOR_BGR2RGB))
            ax2.set_title('Egg count %s' % count)
            ax2.set_yticks([])
            ax2.set_xticks([])

            if save_images:
                if not os.path.isdir(base_file):
                    os.mkdir(base_file)
                plt.savefig(posixpath.join(base_file, str(block_count) + ext),
                            bbox_inches='tight', dpi=dpi)
            try:
                if show_plots:
                    plt.show()
                    plt.waitforbuttonpress(timeout=-1)
            except tk.TclError:
                print("Program exited")
                break
            plt.close(fig)
        block_count += 1
    end_time = time.time()
    count_list.append(("Total Eggs counted {} in {} seconds".
          format(total_egg_count, round((end_time - start_time), 2))))
    with open(posixpath.join(base_file, "count.txt"), "w") as f:
        for s in count_list:
            f.write(str(s) + "\n")
    with open(posixpath.join(base_file, "egg_list.txt"), "w") as f:
        for s in egg_list:
            f.write(str(s) + "\n")
    print("Total Eggs counted {} in {} seconds".
          format(total_egg_count, round((end_time - start_time), 2)))
