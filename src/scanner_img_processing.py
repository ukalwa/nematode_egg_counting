# -*- coding: utf-8 -*-
"""
Created on Thu Apr 20 17:31:37 2017

@author: ukalwa
"""
import sys, argparse
import os
import posixpath
import Tkinter as tk
import tkFileDialog as filedialog
import json

from process_whole_image import process_whole_image

root = tk.Tk()
root.withdraw()

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


def main(dir_path='', file_path='', process_dir=False, search_string=None):
    global save_images, show_plots, create_plots, obj
    if process_dir:
        if len(dir_path) == 0:
                dir_path = filedialog.askdirectory(
                        initialdir=r'Y:\EggCounting\Images\Scanner Images')
        if len(dir_path) != 0:
            for name in os.listdir(dir_path):
                if not os.path.isdir(name) and name.endswith('.tif') \
                        and search_string in name:
                    file_path = posixpath.join(dir_path, name)
                    print "FILE: %s" % file_path
                    img_list = process_whole_image(file_path=file_path,
                                                   create_plots=create_plots,
                                                   save_images=save_images,
                                                   show_plots=show_plots,
                                                   color=(255, 255, 0),
                                                   obj=obj, save_obj=False)
            return img_list
        else:
            print "Invalid directory"
            return
    else:
        if len(file_path) == 0:
            file_path = filedialog.askopenfilename(
                initialdir=r'Y:\EggCounting\Images\Scanner Images')
        if len(file_path) != 0:
            img_list = process_whole_image(file_path=file_path,
                                           create_plots=create_plots,
                                           save_images=save_images,
                                           show_plots=show_plots,
                                           color=(255, 255, 0),
                                           obj=obj, save_obj=False)
            return img_list
        else:
            print "Invalid file"
            return




# Main process starts here
if __name__ == "__main__":
    usage = ("Usage python scanner_img_processing.py "
             "[-d <dir> -s <search string> or -f <full file path>]")
    if len(sys.argv) == 1:
        print "Optional " + usage
        main(process_dir=False)
    else:
        parser = argparse.ArgumentParser()
        parser.add_argument("-d", "--dir", help="directory containing files")
        parser.add_argument("-f", "--file", help="full file path")
        parser.add_argument("-s", "--search", help="search string")
        args = parser.parse_args()
        if args.dir and args.search:
            if os.path.isdir(args.dir):
                img_list = main(dir_path=args.dir, search_string=args.search,
                                process_dir=True)
                print "Program exited"
            else:
                print "Invalid directory, using UI to get directory"
                img_list = main(process_dir=True)
        elif args.file:
            if os.path.isfile(args.file):
                main(file_path=args.file, process_dir=False)
            else:
                print "file does not exist, using UI to get filepath"
                img_list = main(process_dir=False)
        elif args.dir and not args.search:
            print usage
            print "Program exited"
