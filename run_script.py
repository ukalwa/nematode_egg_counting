# -*- coding: utf-8 -*-
"""
The script processes a single file or a batch in a directory specified by the
command line arguments

Created on Thu Apr 20 17:31:37 2017

@author: ukalwa
"""
# Compatibility with Python 2 and Python 3
from __future__ import print_function

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
from src.process_image import process_image  # noqa: E402
from src.utilities import validate_file  # noqa: E402

root = Tk()
root.withdraw()

obj = {"sizes": [], "detected": [], "mean": []}


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
    global obj
    if process_dir:
        if len(dir_path) == 0:  # using UI to get directory
            dir_path = filedialog.askdirectory(
                initialdir=r'Y:\EggCounting\Images\Scanner Images')
        if len(dir_path) == 0:  # uigetdir operation cancelled
            raise FileNotFoundError("Directory not found")
        images = []
        for name in os.listdir(dir_path):
            file_path = os.path.join(dir_path, name)

            if validate_file(file_path):
                if search_string is not None:
                    if search_string in name:
                        print("FILE: %s" % file_path)
                        process_image(file_path=file_path, obj=obj,
                                      save_obj=False)
                else:
                    print("FILE: %s" % file_path)
                    process_image(file_path=file_path, obj=obj, save_obj=False)
        return images
    else:
        if len(file_path) == 0:  # using UI to get file
            file_path = filedialog.askopenfilename(
                initialdir=r'Y:\EggCounting\Images\Scanner Images')
        if len(file_path) == 0:  # uigetfile operation cancelled
            raise FileNotFoundError("File not found")
        print("FILE: %s" % file_path)
        process_image(file_path=file_path, obj=obj, save_obj=False)


# Main process starts here
if __name__ == "__main__":
    usage = '''    
    Usage `python run_script.py [<Command> <Value>]`

        Command     Value                [Description]
        -uf                              Navigate through GUI to get file
        -ud                              Navigate through GUI to get directory
        -d          <directory path>     Process files in entire directory
        -p          <pattern string>     Process files matching this pattern
        -f          <file path>          Process file specified by path
        -ns                              Don't save images
        -h                               Show this help message and exit

        Warning: Specifying only directory processes all the files in the
        directory. However, If you want to process some files with a specific
        pattern include -p <pattern matching string> argument when running 
        with directory option
    '''
    warn_usage = '''
        Warning: No pattern provided, the script will process all
        image files in the directory
    '''

    if len(sys.argv) == 1:
        print(usage)
        main(process_dir=False)
    else:
        parser = argparse.ArgumentParser(add_help=False)
        parser.add_argument("-uf", "--uif", help="Use GUI to get file",
                            action='store_true')
        parser.add_argument("-ud", "--uid", help="Use GUI to get directory",
                            action='store_true')
        parser.add_argument("-d", "--dir", help="directory containing files")
        parser.add_argument("-f", "--file", help="full file path")
        parser.add_argument("-p", "--pattern", help="Pattern")
        parser.add_argument("-ns", "--nosave", help="Don't save files",
                            action='store_true')
        parser.add_argument('-h', '--help', action='store_true',
                            help='show this help message and exit')
        try:
            args = parser.parse_args()
            if args.help:
                print(usage)
            elif args.uif:
                main(process_dir=False)
            elif args.uid:
                main(process_dir=True)
            else:
                if args.nosave:
                    save_images = False
                if args.dir and args.pattern:
                    if not os.path.isdir(args.dir):
                        raise FileNotFoundError("Directory not found {}".
                                                format(args.dir))
                    img_list = main(dir_path=args.dir,
                                    search_string=args.pattern,
                                    process_dir=True)
                elif args.file:
                    if not validate_file(args.file):
                        raise FileNotFoundError("File not found {}".
                                                format(args.file))
                    main(file_path=args.file, process_dir=False)
                elif args.dir and not args.pattern:
                    if not os.path.isdir(args.dir):
                        raise FileNotFoundError("Directory not found {}".
                                                format(args.dir))
                    print(warn_usage)
                    img_list = main(dir_path=args.dir, process_dir=True)
        except SystemExit:
            print(usage)
