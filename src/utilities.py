"""
Helper functions to assist the programs

Created on Tue Jun 06 12:56:53 2018

@author: ukalwa
"""
# Compatibility with Python 2 and Python 3
from __future__ import generators
# Built-in imports
import os

# third-party imports
import cv2
import numpy as np


def validate_file(file_name):
    if not os.path.isdir(file_name) \
            and (file_name.endswith('.tif')
                 or file_name.endswith('.jpg')):
        return True
    return False


def split_image_into_blocks(file_path, img_list, block_size):
    base_mean = None
    if os.path.exists(file_path):
        img = cv2.imread(file_path)
        if img is not None:
            hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            base_mean = np.array(cv2.mean(hsv))[:-1] / 255
            shape = np.array(img.shape, dtype=float)[:-1]
            if shape[0] < block_size[0] or shape[1] < block_size[1]:
                return 'Block size greater than image size'
            w = int(np.ceil(shape[0] / block_size[0]))
            h = int(np.ceil(shape[1] / block_size[1]))

            for i in range(w):
                for j in range(h):
                    #        print i,j, i*1024, shape[0], j*1024, shape[1]
                    if i * block_size[0] < shape[0] \
                            and j * block_size[1] < shape[1]:
                        img_list.append(
                            img[i * block_size[0]:(i + 1) * block_size[0],
                            j * block_size[1]:(j + 1) * block_size[1], :])
                    elif i * block_size[0] < shape[0] \
                            and not j * block_size[1] < shape[1]:
                        img_list.append(
                            img[i * block_size[0]:(i + 1) * block_size[0],
                            j * block_size[1]:, :])
                    elif not i * block_size[0] < shape[0] \
                            and j * block_size[1] < shape[1]:
                        img_list.append(img[i * block_size[0]:,
                                        j * block_size[1]:(j + 1) *
                                                          block_size[1], :])
                    else:
                        img_list.append(
                            img[i * block_size[0]:, j * block_size[1]:, :])
            return ['', base_mean]
        else:
            return ['Invalid file', base_mean]
    else:
        return ['Invalid file', base_mean]


def detect_obj(mask, cfg_file=None, block=-1):
    if not cfg_file:
        # Parse configuration file
        config = configparser.ConfigParser()
        CFGPATH = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                               'config.ini')
        config.read(CFGPATH)
    else:
        config = cfg_file

    # blob identification params
    min_s = config.getfloat("blob", "min_shape")
    max_s = config.getfloat("blob", "max_shape")
    min_w = config.getfloat("blob", "min_width")
    max_w = config.getint("blob", "max_width")
    min_h = config.getfloat("blob", "min_height")
    min_area = config.getint("blob", "min_area")
    max_area = config.getint("blob", "max_area")
    im2, contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE,
                                                cv2.CHAIN_APPROX_NONE)

    obj_params = []
    count = 0
    obj_cnt = []
    for k in range(len(contours)):
        cnt = contours[k]
        if min_area <= cv2.contourArea(cnt) <= max_area:
            rect = cv2.minAreaRect(cnt)
            (object_w, object_h) = (round(max(rect[1]), 2),
                                    round(min(rect[1]), 2))

            if min_s <= round(object_w / object_h, 2) <= max_s \
                    and min_w <= object_w < max_w and object_h >= min_h:
                obj_params.append(
                    "{}, {}, {}, {}, {}".format(
                        block, cv2.contourArea(cnt),
                        object_w, object_h,
                        round(object_w / object_h, 2)))

                obj_cnt.append(cnt)
                count += 1
    return {"count": count, "contours": obj_cnt, "obj_params": obj_params}


def draw_box(image, contours, color=(255, 255, 0), thickness=2):
    for k in range(len(contours)):
        cnt = contours[k]
        rect = cv2.minAreaRect(cnt)
        box = np.int0(cv2.boxPoints(rect))
        cv2.drawContours(image, [box], 0, color, thickness)


def add_text_to_box(image, contours, color=(0, 255, 255), thickness=1,
                 font=cv2.FONT_HERSHEY_SIMPLEX, font_scale = 0.5,
                 offset=(10,10)):
    for i in range(len(contours)):
        cnt = contours[i]
        M = cv2.moments(cnt)
        cx = int(M['m10'] / M['m00'])
        cy = int(M['m01'] / M['m00'])
        cv2.putText(image, params, (cx - offset[0], cy - offset[1]), font,
                    font_scale, color, thickness)
