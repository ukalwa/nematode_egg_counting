# -*- coding: utf-8 -*-
"""
Created on Tue Apr 25 15:06:59 2017

@author: ukalwa
"""
# Built-in imports
from __future__ import print_function, division
import os
import sys

if sys.version_info[0] < 3:
    import ConfigParser as configparser
else:
    import configparser

# third-party imports
import cv2  # noqa: E402
import numpy as np  # noqa: E402


def process_block_image(b_img, obj_parameters_list, base_mean,
                        obj, retr_objects=False, cfg_file=None):
    if not cfg_file:
        # Parse configuration file
        config = configparser.ConfigParser()
        CFGPATH = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                               'config.ini')
        config.read(CFGPATH)
    else:
        config = cfg_file

    mean_thresh = config.getfloat('DEFAULT', 'mean_thresh')
    count = 0

    # blob identification params
    min_s = config.getfloat("blob", "min_shape")
    max_s = config.getfloat("blob", "max_shape")
    min_w = config.getfloat("blob", "min_width")
    max_w = config.getint("blob", "max_width")
    min_h = config.getfloat("blob", "min_height")
    min_area = config.getint("blob", "min_area")
    max_area = config.getint("blob", "max_area")

    # box params
    color = tuple([int(item) for item in config.get("box", "color").
                  split(",")])
    thickness = config.getint("box", "thickness")

    if retr_objects:
        obj_sizes = obj['sizes']
        objects_detected = obj['detected']
        obj_mean = obj['mean']
    else:
        obj_sizes = []
        objects_detected = []
        obj_mean = []
    # To detect top and interface
    if base_mean[1] < mean_thresh:
        layer = "top"

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
    im2, contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE,
                                                cv2.CHAIN_APPROX_NONE)

    for k in np.arange(len(contours)):
        cnt = contours[k]
        if min_area <= cv2.contourArea(cnt) <= max_area:
            rect = cv2.minAreaRect(cnt)
            (object_w, object_h) = (round(max(rect[1]), 2),
                                    round(min(rect[1]), 2))

            if min_s <= round(object_w / object_h, 2) <= max_s \
                  and min_w <= object_w < max_w and object_h >= min_h:
                # print(cv2.contourArea(cnt), object_w, object_h,
                #       round(object_w / object_h, 2))
                obj_parameters_list.append("A = %s, W = %s, H = %s, W/H = %s"
                                           % (cv2.contourArea(cnt),
                                              object_w, object_h,
                                              round(object_w / object_h, 2)))
                if retr_objects:
                    # bound_rect = map(sum,zip(cv2.boundingRect(cnt),img_tol))
                    bound_rect = cv2.boundingRect(cnt)
                    extracted_obj = b_img[bound_rect[1]:bound_rect[1]
                                                        + bound_rect[3],
                                    bound_rect[0]:bound_rect[0]
                                                  + bound_rect[2]].copy()
                    obj_hsv = cv2.cvtColor(extracted_obj, cv2.COLOR_BGR2HSV)
                    objects_detected.append(extracted_obj)
                    obj_sizes.append(bound_rect[2:])
                    obj_mean.append([np.array(cv2.mean(extracted_obj))[:-1],
                                     np.array(cv2.mean(obj_hsv))[:-1]])

                box = np.int0(cv2.boxPoints(rect))
                cv2.drawContours(b_img, [box], 0, color, thickness)
                count += 1
        else:
            continue
    return {'img': b_img, 'count': count}
