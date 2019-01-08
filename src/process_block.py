# -*- coding: utf-8 -*-
"""
Module containing methods to processes a single block

saved on Tue Apr 25 15:06:59 2017

@author: ukalwa
"""
# Built-in imports
from __future__ import division, generators
import os
import sys

try:
    import configparser
except ImportError:
    import ConfigParser as configparser

# third-party imports
import cv2
import numpy as np

# Custom module imports
from src.utilities import get_obj_params, draw_box


def process_block(block, base_mean, file_name="",
                  cfg_file=None, logger=None, blk_cnt=-1):
    """
    This function processes a block by utilizing helper functions and
    using config parameters extracted from configuration file

    :param block: sub image as 3-d numpy array
    :param base_mean: image mean to set the thresholds for different layers
    :param cfg_file: config file containing all configuration settings
    :param logger: for logging status
    :param blk_cnt: block number for reference (default=-1)
    :return: dict containing processed block, egg counts, and egg params
    :rtype: dict
    """
    if not cfg_file:
        # Parse configuration file
        config = configparser.ConfigParser()
        CFGPATH = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                               'config.ini')
        config.read(CFGPATH)
    else:
        config = cfg_file

    # File name used to link blocks to original image
    if file_name:
        # To ensure file_name only has base name instead of absolute path
        file_name = os.path.basename(file_name)

    mean_thresh = config.getfloat('DEFAULT', 'mean_thresh')


    # box params
    color = tuple([int(item) for item in config.get("box", "color").
                  split(",")])
    thickness = config.getint("box", "thickness")

    # fig params
    save = config.getboolean("fig", "save")

    # To detect top and interface
    if base_mean[1] < mean_thresh:
        layer = "interface"

    else:
        layer = "pellet"

    hsv_low = [int(item) for item in config.get(layer, "hsv_min").split(",")]
    hsv_high = [int(item) for item in config.get(layer, "hsv_max").split(",")]

    hsv_low = np.array(hsv_low, dtype=np.float32) / 255
    hsv_high = np.array(hsv_high, dtype=np.float32) / 255

    # base_mean = (0.53, 0.07, 0.88)
    block_hsv = np.float32(cv2.cvtColor(block, cv2.COLOR_BGR2HSV))
    b_image_hsv = block_hsv / np.max(block_hsv)

    # apply the hsv range on a mask
    mask = cv2.inRange(b_image_hsv, hsv_low, hsv_high)

    # Detect objects with the criteria specified in config file
    result = get_obj_params(mask, cfg_file=config, block=blk_cnt)

    # Overlay the block with detected contours
    if save:
        draw_box(block, result["contours"], color=color, thickness=thickness)

    return {'img': block, 'count': result["count"], 'mask': mask,
            "obj_params": result["obj_params"], "contours": result["contours"]}
