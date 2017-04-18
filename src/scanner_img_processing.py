# -*- coding: utf-8 -*-
"""
Created on Mon Apr 03 15:04:43 2017

@author: ukalwa
"""
import cv2
import numpy as np
import matplotlib.pyplot as plt
plt.style.use('ggplot')
import time
import Tkinter as tk
import tkFileDialog as filedialog

img_list = [] # Images are split into blocks and saved as list of arrays
counter = 0 # Total Egg count initialization to 0
block_count = 0 # To store current block
show_plots = True # Set it to True to check the plots
    
    
root = tk.Tk()
root.withdraw()
file_path = filedialog.askopenfilename(initialdir='../../Images/Scanner Images/')

if len(file_path) != 0:
    start_time = time.time()
    img = cv2.imread(file_path)
    shape = np.array(img.shape,dtype=float)[:-1]
    w,h = np.int16(np.ceil(shape/1024))
    
    
    def process_block_image(b_img,color):
        count = 0
        b_img = cv2.medianBlur(b_img,5)
        b_img_hsv = np.float32(cv2.cvtColor(b_img,cv2.COLOR_BGR2HSV))
        b_img_hsv = b_img_hsv/np.max(b_img_hsv)
        BW = np.uint8(cv2.split(b_img_hsv)[1] > 0.5)
    #    b_image = cv2.bitwise_and(b_img,b_img,mask=BW)
        b_image_hsv = cv2.bitwise_and(b_img_hsv,b_img_hsv,mask=BW)
        HSVLOW=np.array([100,0,125],dtype=np.float32)/255
        HSVHIGH=np.array([160,255,200],dtype=np.float32)/255
    
        #apply the range on a mask
        mask = cv2.inRange(b_image_hsv,HSVLOW, HSVHIGH)
        im2, contours, hierarchy = cv2.findContours(mask,cv2.RETR_TREE,cv2.CHAIN_APPROX_NONE)
    #    area = [cv2.contourArea(cnt) for cnt in contours]
        for k in np.arange(len(contours)):
            cnt = contours[k]
            if 50 < cv2.contourArea(cnt) < 85:
                rect = cv2.minAreaRect(cnt)
                (object_w,object_h) = (max(rect[1]),min(rect[1]))
                print object_w, object_h, object_w/object_h
                box = np.int0(cv2.boxPoints(rect))
                cv2.drawContours(b_img,[box],0,color,2)
                count += 1
            else:
                continue
        return b_img, count
      
    
    for i in np.arange(w):
        for j in np.arange(h):
    #        print i,j, i*1024, shape[0], j*1024, shape[1]
            if i*1024 < shape[0] and j*1024 < shape[1]:
                img_list.append(img[i*1024:(i+1)*1024,j*1024:(j+1)*1024,:])
            elif i*1024 < shape[0] and not j*1024 < shape[1]:
                img_list.append(img[i*1024:(i+1)*1024,j*1024:,:])
            elif not i*1024 < shape[0] and j*1024 < shape[1]:
                img_list.append(img[i*1024:,j*1024:(j+1)*1024,:])
            else:
                img_list.append(img[i*1024:,j*1024:,:])
                   
    
    for block_image in img_list:
        b_img = block_image.copy()
        processed_image,count = process_block_image(b_img,(0,255,0))
        counter += count
        block_count +=  1
        print "Image Block %s Egg count %s" %(block_count,count)
        
        if show_plots:
            plt.subplot(1, 2, 1)
            plt.imshow(block_image)
            plt.title('Original Image'), plt.xticks([]), plt.yticks([])
            
            plt.subplot(1, 2, 2)
            plt.imshow(processed_image)
            plt.title('Processed Image'), plt.xticks([]), plt.yticks([])
            
            plt.show()
            plt.waitforbuttonpress(timeout=-1)
        
    print "Total Eggs counted %s in %s seconds" %(counter,(time.time()-start_time))
#cv2.imshow("Processed Image", )
#cv2.waitKey(10000)
#cv2.destroyAllWindows()