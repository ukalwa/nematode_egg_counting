# -*- coding: utf-8 -*-
"""
Created on Mon Apr 03 15:04:43 2017

@author: ukalwa
"""
import Tkinter as tk
import tkFileDialog as filedialog
import os

from split_image_into_blocks import split_image_into_blocks

root = tk.Tk()
root.withdraw()
file_path = filedialog.askopenfilename(initialdir='../../Images/Scanner Images/')
base_file = os.path.splitext(file_path)[0]


img_list = []
block_size = (1024,1024)
status = split_image_into_blocks(file_path, img_list, block_size)
if len(status) != 0:
        print status

#%%
import cv2
import numpy as np

b_img = img_list[282].copy()
color = (0,255,255)
count = 0
hsv_low=np.array([140,135,100],dtype=np.float32)/255
hsv_high=np.array([165,255,215],dtype=np.float32)/255
base_mean = (0.53, 0.07, 0.88)
#    b_img = cv2.medianBlur(b_img,5)
b_img_hsv = np.float32(cv2.cvtColor(b_img,cv2.COLOR_BGR2HSV))
b_img_hsv = b_img_hsv/np.max(b_img_hsv)
BW = np.uint8(cv2.split(b_img_hsv)[1] > 0.5)
#    b_image = cv2.bitwise_and(b_img,b_img,mask=BW)
b_image_hsv = cv2.bitwise_and(b_img_hsv,b_img_hsv,mask=BW)

mean = np.round(np.array(cv2.mean(b_img_hsv))[:-1],3)
tolerance_factor = (0.05, 1.5, 7)
tolerance = np.array((1+tolerance_factor*(mean-base_mean)/base_mean),
                     dtype=np.float32)
#if tolerance[2] < 1:
#    hsv_low = hsv_low*tolerance
#    hsv_high[2] = hsv_high[2]*tolerance[2] 
#    hsv_high[2] = 1 if hsv_high[2]*tolerance[2] > 1 else hsv_high[2]
##elif 1 < tolerance[2] < 1.03:
##    tolerance[2] = tolerance[2] - 2*(tolerance[2]-1)
##    hsv_low = hsv_low*tolerance
##    hsv_high[2] = hsv_high[2]*(tolerance[2] - 0.05)
##    hsv_high[2] = 1 if hsv_high[2]*tolerance[2] > 1 else hsv_high[2]
#else:
hsv_low[1] = hsv_low[1]*tolerance[1]
#apply the hsv range on a mask
mask = cv2.inRange(b_image_hsv,hsv_low, hsv_high)
im2, contours, hierarchy = cv2.findContours(mask,cv2.RETR_TREE,
                                            cv2.CHAIN_APPROX_NONE)
area = [cv2.contourArea(cnt) for cnt in contours]
for k in np.arange(len(contours)):
    cnt = contours[k]
    if 40 <= cv2.contourArea(cnt) <= 135:
        rect = cv2.minAreaRect(cnt)
        (object_w,object_h) = (round(max(rect[1]),2),
                                 round(min(rect[1]),2))
#        print k, object_w, object_h, round(object_w/object_h,2)
        if 1.78 <= round(object_w/object_h,2) <= 3.3 and 12 < object_w < 22:
            print object_w, object_h, round(object_w/object_h,2)
#            obj_parameters_list.append("%s, %s, %s" %(object_w, object_h, 
#                                        round(object_w/object_h,2)))
#            box = np.int0(cv2.boxPoints(rect))
#            cv2.drawContours(b_img,[box],0,color,2)
            count += 1
    else:
        continue
    
#%%
import matplotlib.pyplot as plt
plt.style.use('dark_background')

from process_block_image import process_block_image

color = (0,255,255)
count_list = []
show_plots = True
b_img = img_list[45].copy()
processed_image, count = process_block_image(b_img, color, count_list)
print "Egg count %s" %(count)
#plt.ioff()

if show_plots:
    fig = plt.figure(figsize=(8.0, 5.0))
    fig.add_subplot(121).imshow(b_img)
    fig.add_subplot(121).set_title('Original Image'), plt.xticks([]), plt.yticks([])
#    plt.subplot(1, 2, 1)
#    plt.imshow(img_list[296].copy())
#    plt.title('Original Image'), plt.xticks([]), plt.yticks([])
    
#    plt.subplot(1, 2, 2)
#    plt.imshow(processed_image)
#    plt.title('Processed Image'), plt.xticks([]), plt.yticks([])
    fig.add_subplot(122).imshow(processed_image)
    fig.add_subplot(122).set_title('Egg count %s' %count), plt.xticks([]), plt.yticks([])
    
    fig.show()
    try:
        fig.waitforbuttonpress(timeout=-1)
        base_file = os.path.splitext(file_path)[0]
#        fig.savefig(base_file+'1'+'.png', bbox_inches='tight', dpi=200)
    except tk.TclError:
        print "Program exited"


#%%
import cv2
import numpy as np

counter = 0
temp_img = np.copy(img_list[57])
hsv_image = cv2.cvtColor(temp_img,cv2.COLOR_BGR2HSV)
#hsv_low = np.array([110,80,0])
#hsv_high = np.array([165,255,133])

hsv_low = np.array([123,75,0])
hsv_high = np.array([255,255,200])

lab_low = np.array([0,160,0])
lab_high = np.array([255,255,100])
mask = cv2.inRange(hsv_image,hsv_low, hsv_high)
res = cv2.bitwise_and(temp_img,temp_img, mask =mask)
im2, contours, hierarchy = cv2.findContours(mask,cv2.RETR_TREE,cv2.CHAIN_APPROX_NONE)
#area = np.array([cv2.contourArea(cnt) for cnt in contours])
contours = np.array(contours)[np.logical_and(area>35, area<90)].tolist()
temp_mask = np.zeros(hsv_image.shape[:-1],np.uint8)
#cv2.namedWindow('Processed Image',cv2.WINDOW_NORMAL)
#cv2.namedWindow('Original Image',cv2.WINDOW_NORMAL)
new_contours = []
for i in xrange(0,len(contours)): 
    rect = cv2.minAreaRect(contours[i])
    (object_w,object_h) = (min(rect[1]),max(rect[1]))
    print object_w,object_h, object_w/object_h
    if object_w < 4 or object_w > 8.5 or object_w/object_h < 0.35 \
    or object_w/object_h > 0.75 :
        continue
    temp_mask[...]=0
    cv2.drawContours(temp_mask,contours,i,(255,255,255),-1)
    
    if cv2.mean(hsv_image,temp_mask)[1]>190 or cv2.mean(hsv_image,temp_mask)[2]>160:
        continue
    print cv2.mean(hsv_image,temp_mask)
    res = cv2.bitwise_and(temp_img,temp_img, mask =temp_mask)
    new_contours.append(contours[i])
#    font = cv2.FONT_HERSHEY_SIMPLEX
#    #cv2.putText(temp_img,'Frame Number %s/256' %(len(img_list)-1),(10,100), font, 1,(255,255,0),2)
#    cv2.putText(res,'Eggs found %s' %(len(contours)),(500,100), font, 1,(255,255,0),2)
#    cv2.imshow("Processed Image",res)
#    cv2.imshow("Original Image",temp_img)
    if cv2.waitKey(50000) == 32:
        continue
    

counter += len(new_contours)
print len(img_list)-1, len(new_contours)
cv2.drawContours(temp_img,new_contours,-1,(150,0,0),2)
cv2.imshow("Processed Image",temp_img)
cv2.waitKey(50000)
cv2.destroyAllWindows()
print "No of eggs found: %s" %counter
#cv2.drawContours(temp_img,contours,-1,(255,255,0),2)
#cv2.namedWindow('Image',cv2.WINDOW_NORMAL)


#%%
import my_modules as m
counter = 0;
temp_img = np.copy(img_list[39])
hsv_image = cv2.cvtColor(temp_img,cv2.COLOR_BGR2HSV)
#gray_image = cv2.cvtColor(temp_img,cv2.COLOR_BGR2GRAY)
#thresh = cv2.adaptiveThreshold(hsv_image[:,:,2],255,cv2.ADAPTIVE_THRESH_MEAN_C,cv2.THRESH_BINARY_INV,7,2)
#im2, contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_NONE)
#area = np.array([cv2.contourArea(cnt) for cnt in contours])
mouse_events = m.Mouse_Events()
cv2.namedWindow("Image")
cv2.setMouseCallback("Image",mouse_events.mouse_click)
#cv2.imshow("Image",b_img)
#print hsv_image[:,:,1][mouse_events.point]
cv2.imshow("Original Image",temp_img)
cv2.waitKey(10000)
cv2.destroyAllWindows()



#%%
import matplotlib.pyplot as plt
plt.style.use('ggplot')
from process_block_image import process_block_image

counter = 0
block_count = 0
show_plots = True
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
    
print counter
#cv2.imshow("Processed Image", )
#cv2.waitKey(10000)
#cv2.destroyAllWindows()
        



    
    














