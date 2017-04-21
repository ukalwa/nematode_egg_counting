# -*- coding: utf-8 -*-
"""
Created on Mon Apr 03 15:04:43 2017

@author: ukalwa
"""
import os
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
create_plots = True
show_plots = False # Set it to True to check the plots
save_images = True
if not show_plots:
    plt.ioff() 
    
root = tk.Tk()
root.withdraw()
file_path = filedialog.askopenfilename(initialdir='../../Images/Scanner Images/')
base_file = os.path.splitext(file_path)[0]

def process_block_image(b_img,color):
    count = 0
#    b_img = cv2.medianBlur(b_img,5)
    b_img_hsv = np.float32(cv2.cvtColor(b_img,cv2.COLOR_BGR2HSV))
    b_img_hsv = b_img_hsv/np.max(b_img_hsv)
    BW = np.uint8(cv2.split(b_img_hsv)[1] > 0.5)
#    b_image = cv2.bitwise_and(b_img,b_img,mask=BW)
    b_image_hsv = cv2.bitwise_and(b_img_hsv,b_img_hsv,mask=BW)
    hsv_low=np.array([100,0,125],dtype=np.float32)/255
    hsv_high=np.array([160,255,200],dtype=np.float32)/255

    #apply the range on a mask
    mask = cv2.inRange(b_image_hsv,hsv_low, hsv_high)
    im2, contours, hierarchy = cv2.findContours(mask,cv2.RETR_TREE,cv2.CHAIN_APPROX_NONE)
#    area = [cv2.contourArea(cnt) for cnt in contours]
    for k in np.arange(len(contours)):
        cnt = contours[k]
        if 50 < cv2.contourArea(cnt) < 85:
            rect = cv2.minAreaRect(cnt)
            (object_w,object_h) = (max(rect[1]),min(rect[1]))
            if 12 < object_w < 16 and 5 < object_h < 8 and 50 < object_w*object_h < 85:
                print object_w, object_h, object_w/object_h
                box = np.int0(cv2.boxPoints(rect))
                cv2.drawContours(b_img,[box],0,color,3)
                count += 1
        else:
            continue
    return b_img, count
    
if len(file_path) != 0:
    start_time = time.time()
    img = cv2.imread(file_path)
    shape = np.array(img.shape,dtype=float)[:-1]
    w,h = np.int16(np.ceil(shape/1024))
      
    
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
        processed_image,count = process_block_image(b_img,(0,0,0))
        counter += count
        block_count +=  1
        print "Image Block %s Egg count %s" %(block_count,count)
        
        if create_plots:
            fig = plt.figure(figsize=(8.0, 5.0))
            fig.add_subplot(121).imshow(block_image)
            fig.add_subplot(121).set_title('Original Image'), plt.xticks([]), plt.yticks([])
            
            fig.add_subplot(122).imshow(processed_image)
            fig.add_subplot(122).set_title('Processed Image'), plt.xticks([]), plt.yticks([])
            
            
            try:
                if show_plots:
                    plt.show()
                    plt.waitforbuttonpress(timeout=-1)
                if save_images:
                    if not os.path.exists(base_file):
                        os.mkdir(base_file)
                    plt.savefig(base_file+'/'+str(block_count)+'.png', bbox_inches='tight', dpi = 200)
                
            except tk.TclError:
                break
                print "Program exited"
            plt.close(fig)
    print "Total Eggs counted %s in %s seconds" %(counter,(time.time()-start_time))
#cv2.imshow("Processed Image", )
#cv2.waitKey(10000)
#cv2.destroyAllWindows()