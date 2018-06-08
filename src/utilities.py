"""
Helper functions to assist the main functions

Created on Tue Jun 06 12:56:53 2018

@author: ukalwa
"""
# Compatibility with Python 2 and Python 3
from __future__ import generators, division
# Built-in imports
import os

# third-party imports
import cv2
import numpy as np


def validate_file(file_name):
    """
    Checks if the file exists and it is an image file (TIFF or JPGEG)

    :param file_name: absolute path of the file
    :return: True if is an image file and False if it isn't
    :rtype: bool
    """
    if not os.path.isdir(file_name) \
            and (file_name.endswith('.tif')
                 or file_name.endswith('.jpg')):
        return True
    return False


def read_image(file_path):
    """
    Validates the image file, reads and returns it as a 3-d numpy array

    :param file_path: absolute path of the file
    :return: image as 3-d numpy array
    """
    if not validate_file(file_path):
        raise FileNotFoundError('Invalid file {}'.format(file_path))
    img = cv2.imread(file_path)
    if img is None:
        raise IOError("Unable to read file {}".format(file_path))
    return img


def split_image(img, block_size):
    """
    Splits the image to multiple blocks based on block_size

    :param img: image as 3-d numpy array
    :param block_size: tuple of size 2 (block_width, block_height)
    :return: sub_images as a list
    :rtype: List
    """
    img_list = []
    shape = np.array(img.shape, dtype=float)[:-1]
    if shape[0] < block_size[0] or shape[1] < block_size[1]:
        raise ValueError('Block size greater than image size')
    w = int(np.ceil(shape[0] / block_size[0]))
    h = int(np.ceil(shape[1] / block_size[1]))

    for i in range(w):
        for j in range(h):
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
    return img_list


def detect_obj(mask, cfg_file=None, block=-1):
    """
    Identifies the objects from a binary image based on parameters such as
    width, height, shape, and area specified in the config file.

    :param mask: binary image with potential objects and unwanted blobs
    :param cfg_file: config file with the object identification parameters
    :param block: block number for logging purposes (default=-1)
    :return: return a dict with count and lists of object params and contours
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
    """
    Draws a min area rectangle around the object identified by their boundary
    contours. Since it is an inplace change, it affects the input image which
    is why this method doesn't return anything.

    :param image: image as a numpy array
    :param contours: describing object boundaries as a list of numpy arrays
    :param color: a 3-d tuple specifying BGR colors (default=(255, 255, 0))
    :param thickness: box thickness (default=2)
    """
    for k in range(len(contours)):
        cnt = contours[k]
        rect = cv2.minAreaRect(cnt)
        box = np.int0(cv2.boxPoints(rect))
        cv2.drawContours(image, [box], 0, color, thickness)


def add_text_to_box(image, contours, color=(0, 255, 255), thickness=1,
                 font=cv2.FONT_HERSHEY_SIMPLEX, font_scale=0.5,
                 offset=(10, 10)):
    """
    Adds a label to the objects identified by their boundary contours.

    :param image: image as a numpy array
    :param contours: describing object boundaries as a list of numpy arrays
    :param color: a 3-d tuple specifying BGR colors (default=(0, 255, 255))
    :param thickness: box thickness (default=1)
    :param font: text font (default=cv2.FONT_HERSHEY_SIMPLEX)
    :param font_scale: font scale (default=0.5)
    :param offset: distance from the box as (x_dist, y_dist) (default=(10,10)
    """
    for i in range(len(contours)):
        cnt = contours[i]
        M = cv2.moments(cnt)
        cx = int(M['m10'] / M['m00'])
        cy = int(M['m01'] / M['m00'])
        cv2.putText(image, params, (cx - offset[0], cy - offset[1]), font,
                    font_scale, color, thickness)


def get_mean(image, hsv_mean=False):
    """
    Calculate the mean of the image. Setting hsv_mean=True, this method can
    calculate the mean of the hsv image instead.

    :param image: Image as 3-d numpy array
    :param hsv_mean: True to get hsv image mean (default=False)
    :return: mean of the image
    :rtype: float
    """
    if hsv_mean:
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        return np.array(cv2.mean(hsv))[:-1] / 255
    return np.array(cv2.mean(image))[:-1] / 255
