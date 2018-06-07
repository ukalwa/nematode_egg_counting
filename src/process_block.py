# -*- coding: utf-8 -*-
"""
Created on Tue Apr 25 15:06:59 2017

@author: ukalwa
"""
# Built-in imports
from __future__ import division, generators
import os
import sys

if sys.version_info[0] < 3:
    import ConfigParser as configparser
else:
    import configparser

# third-party imports
import cv2  # noqa: E402
import numpy as np  # noqa: E402

# Custom module imports
from src.utilities import detect_obj, draw_box  # noqa: E402


def process_block(b_img, base_mean, retr_objects=False, cfg_file=None,
                  logger=None, blk_cnt=-1):
    if not cfg_file:
        # Parse configuration file
        config = configparser.ConfigParser()
        CFGPATH = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                               'config.ini')
        config.read(CFGPATH)
    else:
        config = cfg_file

    mean_thresh = config.getfloat('DEFAULT', 'mean_thresh')

    # box params
    color = tuple([int(item) for item in config.get("box", "color").
                  split(",")])
    thickness = config.getint("box", "thickness")

    # fig params
    create = config.getboolean("fig", "create")

    obj = {"sizes": [], "detected": [], "mean": []}
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
    b_img_hsv = np.float32(cv2.cvtColor(b_img, cv2.COLOR_BGR2HSV))
    b_image_hsv = b_img_hsv / np.max(b_img_hsv)

    # apply the hsv range on a mask
    mask = cv2.inRange(b_image_hsv, hsv_low, hsv_high)

    result = detect_obj(mask, cfg_file=config, block=blk_cnt)
    contours = result["contours"]
    if create:
        draw_box(b_img, contours, color=color, thickness=thickness)
    if retr_objects:
        for p in range(len(contours)):
            cnt = contours[p]
            # bound_rect = map(sum,zip(cv2.boundingRect(cnt),img_tol))
            bound_rect = cv2.boundingRect(cnt)
            extracted_obj = b_img[bound_rect[1]:bound_rect[1]
                                                + bound_rect[3],
                            bound_rect[0]:bound_rect[0]
                                          + bound_rect[2]].copy()
            obj_hsv = cv2.cvtColor(extracted_obj, cv2.COLOR_BGR2HSV)
            obj["detected"].append(extracted_obj)
            obj["sizes"].append(bound_rect[2:])
            obj["mean"].append([np.array(cv2.mean(extracted_obj))[:-1],
                                np.array(cv2.mean(obj_hsv))[:-1]])

    return {'img': b_img, 'count': result["count"],
            "obj_params": result["obj_params"], "obj": obj}
