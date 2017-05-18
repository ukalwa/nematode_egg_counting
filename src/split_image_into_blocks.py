# -*- coding: utf-8 -*-
"""
Created on Wed Apr 26 12:05:12 2017

@author: ukalwa
"""
import os
import cv2
import numpy as np


def split_image_into_blocks(file_path, img_list, block_size):
    base_mean = None
    if os.path.exists(file_path):
        img = cv2.imread(file_path)
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
                                    j * block_size[1]:(j + 1) * block_size[1],
                                    :])
                else:
                    img_list.append(
                        img[i * block_size[0]:, j * block_size[1]:, :])
        return ['', base_mean]
    else:
        return ['Invalid file', base_mean]
