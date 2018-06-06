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
            img_list = []
            res = None
            for name in os.listdir(dir_path):
                file_path = os.path.join(dir_path,name)
                if search_string is not None:
                    if not os.path.isdir(file_path) \
                            and (name.endswith('.tif') \
                            or name.endswith('.jpg')) \
                            and (search_string in name if search_string \
                                 is not None else True):
                        print "FILE: %s" % file_path
                        res = process_whole_image(file_path=file_path,
                                               create_plots=create_plots,
                                               save_images=save_images,
                                               show_plots=show_plots,
                                               color=(255, 255, 0),
                                               obj=obj, save_obj=False)
                else:
                    if not os.path.isdir(file_path) \
                            and (name.endswith('.tif') \
                            or name.endswith('.jpg')):
                        print "FILE: %s" % file_path
                        res = process_whole_image(file_path=file_path,
                                               create_plots=create_plots,
                                               save_images=save_images,
                                               show_plots=show_plots,
                                               color=(255, 255, 0),
                                               obj=obj, save_obj=False)
                if res is not None:
                    img_list = res['img']
            return img_list
        else:
            print "Invalid directory"
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
                                           color=(255, 255, 0),
                                           obj=obj, save_obj=False)
            img_list = res['img']
            return img_list
        else:
            print "Invalid file"
            return




# Main process starts here
if __name__ == "__main__":
    usage = '''    Incrorrect arguments passed.

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
        print usage
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
        # print args
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
            elif args.dir and not args.pattern:
                print warn_usage
                img_list = main(dir_path=args.dir, process_dir=True)
