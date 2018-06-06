# -*- coding: utf-8 -*-
"""
The script processes a single file or batch processes all the images in a
directory specified by the command line arguments

Created on Thu Apr 20 17:31:37 2017

@author: ukalwa
"""
# Compatibility with Python 2 and Python 3
from __future__ import print_function, division, with_statement, generators

# Built-in imports
import sys
import argparse
import os
import sys
import posixpath
import json

if sys.version_info[0] < 3:
    from Tkinter import Tk
    import tkFileDialog as filedialog
    import ConfigParser as configparser
else:
    from tkinter import Tk
    from tkinter import filedialog
    import configparser

# Custom module imports
from process_whole_image import process_whole_image  # noqa: E402

root = Tk()
root.withdraw()

create_plots = True
save_images = True
show_plots = False
obj = {'sizes': [], 'detected': []}


def main(dir_path='', file_path='', process_dir=False, search_string=None):
    """
    This method processes a single image or batch processes all the images in a
    specific directory and returns the image list for debugging purposes

    :param dir_path: directory containing the scanned images
    :param file_path: absolute path to the scanned image
    :param process_dir: option to process directory or a single image
    :param search_string: pattern to process scanned images based on it
    :return: List of the cropped egg images detected
    :rtype: List
    """
    global save_images, show_plots, create_plots, obj
    if process_dir:
        if len(dir_path) == 0:
            dir_path = filedialog.askdirectory(
                initialdir=r'Y:\EggCounting\Images\Scanner Images')
        if len(dir_path) != 0:
            images = []
            res = None
            for name in os.listdir(dir_path):
                file_path = os.path.join(dir_path, name)
                if search_string is not None:
                    if not os.path.isdir(file_path) \
                            and (name.endswith('.tif')
                                 or name.endswith('.jpg')) \
                            and (search_string in name
                    if search_string is not None else True):
                        print("FILE: %s" % file_path)
                        res = process_whole_image(file_path=file_path,
                                                  create_plots=create_plots,
                                                  save_images=save_images,
                                                  show_plots=show_plots,
                                                  obj=obj, save_obj=False)
                else:
                    if not os.path.isdir(file_path) \
                            and (name.endswith('.tif')
                                 or name.endswith('.jpg')):
                        print("FILE: %s" % file_path)
                        res = process_whole_image(file_path=file_path,
                                                  create_plots=create_plots,
                                                  save_images=save_images,
                                                  show_plots=show_plots,
                                                  obj=obj, save_obj=False)
                if res is not None:
                    images = res['img']
            return images
        else:
            print("Invalid directory")
            return
    else:
        if len(file_path) == 0:
            file_path = filedialog.askopenfilename(
                initialdir=r'Y:\EggCounting\Images\Scanner Images')
        if len(file_path) != 0:
            res = process_whole_image(file_path=file_path,
                                      create_plots=create_plots,
                                      save_images=save_images,
                                      show_plots=show_plots,
                                      obj=obj, save_obj=False)
            images = res['img']
            return images
        else:
            print("Invalid file")
            return


# Main process starts here
if __name__ == "__main__":
    usage = '''    Incorrect arguments passed.

    Correct Usage `python run_script.py [command value]`

        Command     Value               [Description]
        -u                              Navigate through GUI
        -d          <directory path>    Process files in entire directory
        -p          <pattern string>    Process files matching this pattern
        -f          <file path>         Process file specified by path
        -ns                             Don't save images

        Warning: Specifying only directory processes all the files in the
        directory. However, If you want to process some files with a specific
        pattern include -p <pattern matching string>
        argument when running with directory option
    '''
    warn_usage = '''
        Warning: No pattern provided, the script will process all
        image files in the directory
    '''

    if len(sys.argv) == 1:
        print(usage)
        # main(process_dir=False)
    else:
        parser = argparse.ArgumentParser()
        parser.add_argument("-u", "--ui", help="Navigate with GUI",
                            action='store_true')
        parser.add_argument("-d", "--dir", help="directory containing files")
        parser.add_argument("-f", "--file", help="full file path")
        parser.add_argument("-p", "--pattern", help="Pattern")
        parser.add_argument("-ns", "--nosave", help="Don't save files",
                            action='store_true')
        args = parser.parse_args()
        # print(args
        if args.ui:
            main(process_dir=False)
        else:
            if args.nosave:
                save_images = False
            if args.dir and args.pattern:
                if os.path.isdir(args.dir):
                    img_list = main(dir_path=args.dir,
                                    search_string=args.pattern,
                                    process_dir=True)
                    print("Program exited")
                else:
                    print("Invalid directory, using UI to get directory")
                    img_list = main(process_dir=True)
            elif args.file:
                if os.path.isfile(args.file):
                    main(file_path=args.file, process_dir=False)
                else:
                    print("file does not exist, using UI to get filepath")
                    img_list = main(process_dir=False)
            elif args.dir and not args.pattern:
                print(warn_usage)
                img_list = main(dir_path=args.dir, process_dir=True)
