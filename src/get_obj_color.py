# -*- coding: utf-8 -*-
"""
This module contains methods to interactively find the ranges for color
thresholds to segment an object.

Created on Thu Apr 20 17:31:37 2017

@author: ukalwa
"""
# Built-in imports
from __future__ import print_function, division
import sys

if sys.version_info[0] < 3:
    import Tkinter as tk
    import tkFileDialog as filedialog
else:
    import tkinter as tk
    from tkinter import filedialog

# third-party imports
import cv2  # noqa: E402
import numpy as np  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

# Custom module imports
from utilities import split_image  # noqa: E402
from utilities import detect_obj, draw_box, add_text_to_box  # noqa: E402

plt.style.use('ggplot')

plt.ion()
hsv = None
hh = 'Hue High'
hl = 'Hue Low'
sh = 'Saturation High'
sl = 'Saturation Low'
vh = 'Value High'
vl = 'Value Low'
img_list = []
file_path = None
base_mean = None


# noinspection PyUnusedLocal
def nothing(something=None):
    pass


# noinspection PyUnusedLocal
def onmouse(event, x, y, flags, params):
    global hsv
    if event == cv2.EVENT_LBUTTONDOWN:
        print(x, y, hsv[x, y])


def identify_obj(mask, res):
    """
    Identifies objects in the mask and draws their boundaries on res image

    :param mask: binary image as 2-d numpy array
    :param res: image as a 3-d numpy array
    """
    result = detect_obj(mask)
    contours = result["contours"]
    # Draw bounding box
    draw_box(res, contours)
    # Put text on the box
    add_text_to_box(res, contours)


def get_obj_color(frame):
    """
    This method lets user to interactively update the hsv ranges until he/she \
    is able to fully segment the objects of interest and selects those values \
    for processing future frames.

    :param frame: sub image as 3-d numpy array
    """
    global hsv
    cv2.namedWindow('Original', cv2.WINDOW_NORMAL)
    cv2.namedWindow('Processed', cv2.WINDOW_NORMAL)
    cv2.setMouseCallback('Processed', onmouse)

    cv2.createTrackbar(hl, 'Processed', 140, 255, nothing)
    cv2.createTrackbar(hh, 'Processed', 165, 255, nothing)
    cv2.createTrackbar(sl, 'Processed', 80, 255, nothing)
    cv2.createTrackbar(sh, 'Processed', 255, 255, nothing)
    cv2.createTrackbar(vl, 'Processed', 125, 255, nothing)
    cv2.createTrackbar(vh, 'Processed', 215, 255, nothing)

    while True:
        # convert to HSV from BGR
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # read trackbar positions for all
        hul = cv2.getTrackbarPos(hl, 'Processed')
        huh = cv2.getTrackbarPos(hh, 'Processed')
        sal = cv2.getTrackbarPos(sl, 'Processed')
        sah = cv2.getTrackbarPos(sh, 'Processed')
        val = cv2.getTrackbarPos(vl, 'Processed')
        vah = cv2.getTrackbarPos(vh, 'Processed')
        # make array for final values
        h_s_v_l_o_w = np.array([hul, sal, val])
        h_s_v_h_i_g_h = np.array([huh, sah, vah])

        # apply the range on a mask
        mask = cv2.inRange(hsv, h_s_v_l_o_w, h_s_v_h_i_g_h)
        res = cv2.bitwise_and(frame, frame, mask=mask)
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(res, 's - Select q - Quit',
                    (10, 100), font, 1, (255, 255, 0), 2)
        identify_obj(mask, res)

        cv2.imshow('Original', frame)
        cv2.imshow('Processed', res)
        #    cv2.imshow('yay', frame)
        k = cv2.waitKey(5) & 0xFF
        if k == ord('q'):
            break
        if k == ord('s'):
            cv2.destroyAllWindows()
            return [h_s_v_l_o_w, h_s_v_h_i_g_h]

    cv2.destroyAllWindows()


def select_obj_frame(filename):
    """
    This method reads the image and displays user each block. Then user choses\
    a block with higher objects of interest and enters that block number to\
    use the interactive segmentation method.

    :param filename:
    :return:
    """
    global img_list, base_mean
    block_size = (1024, 1024)

    status, base_mean = split_image(filename, img_list, block_size)
    if len(status) != 0:
        print(status)
        return 1
    frame_no = 0
    for img in img_list:
        rgb_image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        try:
            plt.imshow(rgb_image)
            plt.title('Frame No %s' % frame_no)
            frame_no += 1
            plt.show()
            plt.grid(b=False)
            plt.waitforbuttonpress(.5)
        except:
            break
    inp = raw_input("Enter Frame number : ")
    if len(inp) != 0:
        frame_no = int(inp)
    if 0 <= frame_no < len(img_list):
        get_obj_color(img_list[frame_no])


def open_file():
    """
    Lets user select an image file using file dialog
    """
    global file_path
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(
        initialdir=r'Y:\EggCounting\Images\Scanner Images')
    if len(file_path) != 0:
        select_obj_frame(file_path)


# Run Program
open_file()
