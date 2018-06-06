# -*- coding: utf-8 -*-
"""
This module contains methods to interactively find the ranges for color
thresholds to segment an object.

Created on Thu Apr 20 17:31:37 2017

@author: ukalwa
"""
# Built-in imports
from __future__ import print_function, division

if sys.version_info[0] < 3:
    from Tkinter import Tk
    import tkFileDialog as filedialog
else:
    from tkinter import Tk
    from tkinter import filedialog

# third-party imports
import cv2  # noqa: E402
import numpy as np  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

# Custom module imports
from split_image_into_blocks import split_image_into_blocks  # noqa: E402

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


def detect_obj(mask, res):
    color = (0, 255, 255)
    _, contours, _ = cv2.findContours(mask, cv2.RETR_TREE,
                                      cv2.CHAIN_APPROX_NONE)
    area = [int(cv2.contourArea(cnt)) for cnt in contours]
    for k in np.arange(len(contours)):
        cnt = contours[k]
        if 40 <= cv2.contourArea(cnt) <= 135:
            #        rect = cv2.minAreaRect(cnt)
            rect = cv2.minAreaRect(cnt)
            (object_w, object_h) = (round(max(rect[1]), 2),
                                    round(min(rect[1]), 2))
            # print  object_w, object_h, round(object_w / object_h, 2)
            if 1.78 <= round(object_w / object_h, 2) <= 3.35 \
                    and object_w < 22:
                params = "A:%s W:%s H:%s W/H:%s Pos:%s " % (
                    area[k], object_w, object_h,
                    round(object_w / object_h, 2), k)
                #                print params
                M = cv2.moments(cnt)
                cx = int(M['m10'] / M['m00'])
                cy = int(M['m01'] / M['m00'])
                font = cv2.FONT_HERSHEY_SIMPLEX
                cv2.putText(res, params, (cx - 10, cy - 10), font,
                            0.5, (0, 255, 255), 1)
                # obj_parameters_list.append("%s, %s, %s" %(object_w, object_h,
                #                            round(object_w/object_h,2)))
                box = np.int0(cv2.boxPoints(rect))
                cv2.drawContours(res, [box], 0, color, 2)
        else:
            continue


def get_obj_color(frame):
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
        detect_obj(mask, res)

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
    global img_list, base_mean
    block_size = (1024, 1024)

    status, base_mean = split_image_into_blocks(filename, img_list, block_size)
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
        except tk.TclError:
            break
    inp = raw_input("Enter Frame number : ")
    if len(inp) != 0:
        frame_no = int(inp)
    if 0 <= frame_no < len(img_list):
        get_obj_color(img_list[frame_no])


def open_file():
    global file_path
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(
        initialdir=r'Y:\EggCounting\Images\Scanner Images')
    if len(file_path) != 0:
        select_obj_frame(file_path)


# Run Program
open_file()
