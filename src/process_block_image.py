# -*- coding: utf-8 -*-
"""
Created on Tue Apr 25 15:06:59 2017

@author: ukalwa
"""
import cv2
import numpy as np

def process_block_image(b_img,color):
    count = 0
    obj_parameters_list = []
    hsv_low=np.array([140,170,125],dtype=np.float32)/255
    hsv_high=np.array([165,255,215],dtype=np.float32)/255
#    b_img = cv2.medianBlur(b_img,5)
    b_img_hsv = np.float32(cv2.cvtColor(b_img,cv2.COLOR_BGR2HSV))
    b_img_hsv = b_img_hsv/np.max(b_img_hsv)
    BW = np.uint8(cv2.split(b_img_hsv)[1] > 0.5)
#    b_image = cv2.bitwise_and(b_img,b_img,mask=BW)
    b_image_hsv = cv2.bitwise_and(b_img_hsv,b_img_hsv,mask=BW)
    
    #apply the hsv range on a mask
    mask = cv2.inRange(b_image_hsv,hsv_low, hsv_high)
    im2, contours, hierarchy = cv2.findContours(mask,cv2.RETR_TREE,
                                                cv2.CHAIN_APPROX_NONE)
#    area = [cv2.contourArea(cnt) for cnt in contours]
    for k in np.arange(len(contours)):
        cnt = contours[k]
        if 50 < cv2.contourArea(cnt) < 100:
            rect = cv2.minAreaRect(cnt)
            (object_w,object_h) = (max(rect[1]),min(rect[1]))
            print object_w, object_h, object_w/object_h
            obj_parameters_list.append(object_w, object_h, object_w/object_h)
            box = np.int0(cv2.boxPoints(rect))
            cv2.drawContours(b_img,[box],0,color,2)
            count += 1
        else:
            continue
    return b_img, count, obj_parameters_list