# -*- coding: utf-8 -*-
"""
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
from process_block_image import process_block_image  # noqa: E402
from split_image_into_blocks import split_image_into_blocks  # noqa: E402

plt.style.use('ggplot')


def process_whole_image(file_path, create_plots, save_images,
                        show_plots, obj, save_obj=False):
    start_time = time.time()
    # Images are split into blocks and saved as list of arrays
    config = configparser.ConfigParser()
    CFGPATH = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                           'config.ini')
    config.read(CFGPATH)
    # Block params
    block_size = [int(item) for item in config.get(
        'DEFAULT', 'block_size').split(',')]
    mean_thresh = config.getfloat('DEFAULT', 'mean_thresh')

    # Plot params
    dpi = config.getint("fig", "dpi")
    figsize = [int(item) for item in config.get("fig", "size").split(",")]
    ext = config.get("fig", "ext")
    if not show_plots:
        plt.ioff()

    img_list = []
    # block_size = (1024, 1024)
    counter = 0  # Total Egg count initialization to 0
    block_count = 0  # To store current block
    count_list = []
    egg_list = []
    base_file = os.path.splitext(file_path)[0]
    print("Splitting images into image blocks")
    status, base_mean = split_image_into_blocks(file_path,
                                                img_list, block_size)
    if base_mean is None:
        return
    if base_mean[1] < mean_thresh:
        print("Top or Interface detected")
        count_list.append(["Top or Interface detected"])
    else:
        print("Pellet detected")
        count_list.append(["Pellet detected"])

    if len(status) != 0:
        print(status)
        return 1
    print("Processing all image blocks")
    count_list.append(["Image Block, Egg count"])
    pbar = tqdm(img_list)
    for block_image in pbar:
        pbar.set_description("Egg Count: {}".format(counter))
        b_img = block_image.copy()
        result = process_block_image(b_img, egg_list, base_mean,
                                     obj=obj, retr_objects=save_obj,
                                     cfg_file=config)
        count = result['count']
        processed_image = result['img']
        counter += count
        # print("Image Block %s Egg count %s" % (block_count, count))
        count_list.append("%s, %s" % (block_count, count))

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
                plt.savefig(posixpath.join(base_file, str(block_count)
                                           + ext), bbox_inches='tight',
                            dpi=dpi)

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
    count_list.append("Total Eggs counted %s, %s seconds"
                      % (counter, round((end_time - start_time), 2)))
    with open(posixpath.join(base_file, "count.csv"), "w") as f:
        for s in count_list:
            f.write(str(s) + "\n")
    print("Total Eggs counted %s in %s seconds"
          % (counter, (end_time - start_time)))
    return {'img': img_list, 'counts': count_list, 'eggs': egg_list}
