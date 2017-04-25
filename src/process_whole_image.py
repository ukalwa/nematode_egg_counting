# -*- coding: utf-8 -*-
"""
Created on Tue Apr 25 15:08:53 2017

@author: ukalwa
"""
import os
import posixpath
import time
import Tkinter as tk

import cv2
import numpy as np
import matplotlib.pyplot as plt

from process_block_image import process_block_image

plt.style.use('ggplot')

def process_whole_image(file_path, create_plots, save_images, 
                        show_plots, color):
    if not show_plots:
        plt.ioff()
    img_list = [] # Images are split into blocks and saved as list of arrays
    counter = 0 # Total Egg count initialization to 0
    block_count = 0 # To store current block
    count_list = []
    base_file = os.path.splitext(file_path)[0]
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
            processed_image, count, obj_parameters_list = \
                                            process_block_image(b_img,color)
            counter += count
            block_count +=  1
            print "Image Block %s Egg count %s" %(block_count,count)
            count_list.append("Image Block %s Egg count %s" \
                              %(block_count,count))
            if len(obj_parameters_list) != 0:
                count_list.append(obj_parameters_list)
            
            if create_plots:
                fig = plt.figure(figsize=(8.0, 5.0))
                fig.add_subplot(121).imshow(block_image)
                fig.add_subplot(121).set_title('Original Image'), 
                plt.xticks([]), plt.yticks([])
                
                fig.add_subplot(122).imshow(processed_image)
                fig.add_subplot(122).set_title('Processed Image'), 
                plt.xticks([]), plt.yticks([])
                
                if save_images:
                    if not os.path.isdir(base_file):
                        os.mkdir(base_file)
                    plt.savefig(posixpath.join(base_file,str(block_count)
                                +'.png'), bbox_inches='tight', dpi = 200)
                
                try:
                    if show_plots:
                        plt.show()
                        plt.waitforbuttonpress(timeout=-1)
                except tk.TclError:
                    break
                    print "Program exited"
                plt.close(fig)
        end_time = time.time()
        count_list.append("Total Eggs counted %s in %s seconds" \
                          %(counter,(end_time-start_time)))
        with open(posixpath.join(base_file,"count.txt"), "w") as f:
            for s in count_list:
                f.write(str(s) +"\n")
        print "Total Eggs counted %s in %s seconds" \
                        %(counter,(end_time-start_time))