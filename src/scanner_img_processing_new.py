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
obj = {'sizes': [], 'detected': []}


def process_log(file_name):
    log_path = posixpath.join(file_name, 'Logs')
    json_path = posixpath.join(log_path, 'log.json')
    if not os.path.isdir(log_path):
        os.mkdir(log_path)
    if os.path.isfile(json_path):
        with open(json_path) as data_file:
            data = json.load(data_file)
        print data


# Main process starts here
if process_dir:
    dir_path = filedialog.askdirectory(initialdir='../../Images/')
    if len(dir_path) != 0:
        for name in os.listdir(dir_path):
            if not os.path.isdir(name) and name.endswith('.tif') \
                    and 'new_method' in name:
                file_path = posixpath.join(dir_path, name)
                print file_path
                process_whole_image(file_path=file_path,
                                    create_plots=create_plots,
                                    save_images=True, show_plots=False,
                                    color=(255, 255, 0),
                                    obj=obj, save_obj=True)
    else:
        print "Invalid directory"
else:
    file_path = filedialog.askopenfilename(
        initialdir='../../Images/Scanner Images/')
    if len(file_path) != 0:
        process_whole_image(file_path=file_path,
                            create_plots=create_plots,
                            save_images=True, show_plots=False,
                            color=(255, 255, 0),
                            obj=obj, save_obj=True)
    else:
        print "Invalid file"
