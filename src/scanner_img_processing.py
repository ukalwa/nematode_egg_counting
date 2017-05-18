# -*- coding: utf-8 -*-
"""
Created on Mon Apr 03 15:04:43 2017

@author: ukalwa
"""
import Tkinter as tk
import tkFileDialog as filedialog

from process_whole_image import process_whole_image

root = tk.Tk()
root.withdraw()
file_path = filedialog.askopenfilename(
    initialdir='../../Images/Scanner Images/')
obj = {'sizes': [], 'detected': [], 'mean' : []}


def main():
    if len(file_path) != 0:
        print "FILE: %s" % file_path
        img_list = process_whole_image(file_path=file_path, create_plots=True,
                                       save_images=True, show_plots=False,
                                       color=(255, 255, 0),
                                       obj=obj, save_obj=True)
        return img_list
    else:
        print "Invalid file"
        return []


# Main process starts here
img_list = main()
