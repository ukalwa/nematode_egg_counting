# -*- coding: utf-8 -*-
"""
Created on Thu Apr 20 17:31:37 2017

@author: ukalwa
"""
import os
import posixpath
import Tkinter as tk
import tkFileDialog as filedialog
import json

from process_whole_image import process_whole_image

root = tk.Tk()
root.withdraw()

process_dir = True
create_plots = True
save_images = True
show_plots = False

def process_log(name,status,overwrite_flag):
    LOGPATH = posixpath.join(name,'Logs')
    JSONPATH = posixpath.join(LOGPATH,'log.json')
    if not os.path.isdir(LOGPATH):
        os.mkdir(LOGPATH)
    if os.path.isfile(JSONPATH):
        with open(JSONPATH) as data_file:    
            data = json.load(data_file)
        print data
        
        
## Main process starts here
if process_dir:
    dir_path = filedialog.askdirectory(initialdir='../../Images/')
    if len(dir_path) != 0:
        for name in os.listdir(dir_path):
            if not os.path.isdir(name) and name.endswith('.tif') \
                and 'CL' not in name:
                file_path = posixpath.join(dir_path,name)
                print file_path
                process_whole_image(file_path=file_path, 
                                    create_plots=create_plots, 
                                    save_images=save_images, 
                                    show_plots=show_plots, 
                                    color=(255,255,0))
else:
    file_path = filedialog.askopenfilename(
                    initialdir='../../Images/Scanner Images/')
    if len(file_path) != 0:
        process_whole_image(file_path=file_path, 
                            create_plots=create_plots, 
                            save_images=save_images, 
                            show_plots=show_plots, 
                            color=(255,255,0))
    else:
        print "Invalid file"

