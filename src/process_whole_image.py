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

import matplotlib.pyplot as plt

from process_block_image import process_block_image
from split_image_into_blocks import split_image_into_blocks

plt.style.use('ggplot')


def process_whole_image(file_path, create_plots, save_images,
                        show_plots, color, obj, save_obj=False):
    start_time = time.time()
    if not show_plots:
        plt.ioff()
    img_list = []  # Images are split into blocks and saved as list of arrays
    block_size = (1024, 1024)
    counter = 0  # Total Egg count initialization to 0
    block_count = 0  # To store current block
    count_list = []
    base_file = os.path.splitext(file_path)[0]
    status = split_image_into_blocks(file_path, img_list, block_size)

    if len(status) != 0:
        print status
        return 1

    for block_image in img_list:
        b_img = block_image.copy()
        result = process_block_image(b_img, color, count_list, obj=obj,
                                     retr_objects=save_obj)
        count = result['count']
        processed_image = result['img']
        counter += count
        print "Image Block %s Egg count %s" % (block_count, count)
        count_list.append("Image Block %s Egg count %s"
                          % (block_count, count))

        if create_plots:
            fig = plt.figure(figsize=(8.0, 5.0))
            fig.add_subplot(121).imshow(cv2.cvtColor(block_image,
                                                     cv2.COLOR_BGR2RGB))
            fig.add_subplot(121).set_title('Original Image'),
            plt.xticks([]), plt.yticks([])

            fig.add_subplot(122).imshow(cv2.cvtColor(processed_image,
                                                     cv2.COLOR_BGR2RGB))
            fig.add_subplot(122).set_title('Egg count %s' % count),
            plt.xticks([]), plt.yticks([])

            if save_images:
                if not os.path.isdir(base_file):
                    os.mkdir(base_file)
                plt.savefig(posixpath.join(base_file, str(block_count)
                                           + '.png'), bbox_inches='tight',
                            dpi=200)

            try:
                if show_plots:
                    plt.show()
                    plt.waitforbuttonpress(timeout=-1)
            except tk.TclError:
                break
            print "Program exited"
            plt.close(fig)
        block_count += 1
    end_time = time.time()
    count_list.append("Total Eggs counted %s in %s seconds"
                      % (counter, (end_time - start_time)))
    with open(posixpath.join(base_file, "count.txt"), "w") as f:
        for s in count_list:
            f.write(str(s) + "\n")
    print "Total Eggs counted %s in %s seconds" \
          % (counter, (end_time - start_time))
    return img_list
