# -*- coding: utf-8 -*-
"""
Created on Tue Apr 25 15:06:59 2017

@author: ukalwa
"""
import cv2
import numpy as np


def process_block_image(b_img, color, obj_parameters_list, base_mean,
                        obj, retr_objects=False):
    count = 0
    if retr_objects:
        obj_sizes = obj['sizes']
        objects_detected = obj['detected']
        obj_mean = obj['mean']
    #    img_tol = (-2,-2,2,2)
    hsv_low = np.array([140, 135, 155], dtype=np.float32) / 255
    hsv_high = np.array([165, 255, 225], dtype=np.float32) / 255
    # base_mean = (0.53, 0.07, 0.88)
    #    b_img = cv2.medianBlur(b_img,5)
    b_img_hsv = np.float32(cv2.cvtColor(b_img, cv2.COLOR_BGR2HSV))
    b_img_hsv = b_img_hsv / np.max(b_img_hsv)
    b_w = np.uint8(cv2.split(b_img_hsv)[1] > 0.5)
    #    b_image = cv2.bitwise_and(b_img,b_img,mask=BW)
    b_image_hsv = cv2.bitwise_and(b_img_hsv, b_img_hsv, mask=b_w)

    # mean = np.round(np.array(cv2.mean(b_img_hsv))[:-1], 3)
    # tolerance_factor = (0.05, 1.5, 7)
    # tolerance = np.array(
    #     (1 + tolerance_factor * (mean - base_mean) / base_mean),
    #     dtype=np.float32)
    #    if tolerance[2] < 1:
    #        hsv_low = hsv_low*tolerance
    #        hsv_high[2] = hsv_high[2]*tolerance[2]
    #        hsv_high[2] = 1 if hsv_high[2]*tolerance[2] > 1 else hsv_high[2]
    #    else:
    # hsv_low[1] = hsv_low[1] * tolerance[1]

    # apply the hsv range on a mask
    mask = cv2.inRange(b_image_hsv, hsv_low, hsv_high)
    im2, contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE,
                                                cv2.CHAIN_APPROX_NONE)
    #    area = [cv2.contourArea(cnt) for cnt in contours]
    for k in np.arange(len(contours)):
        cnt = contours[k]
        if 35 <= cv2.contourArea(cnt) <= 135:
            rect = cv2.minAreaRect(cnt)
            (object_w, object_h) = (round(max(rect[1]), 2),
                                    round(min(rect[1]), 2))

            if 1.65 <= round(object_w / object_h, 2) <= 3.35 \
                  and object_w < 22:
                print cv2.contourArea(cnt), object_w, object_h, \
                    round(object_w / object_h, 2)
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
                cv2.drawContours(b_img, [box], 0, color, 2)
                count += 1
        else:
            continue
    return {'img': b_img, 'count': count}
