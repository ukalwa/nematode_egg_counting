**Nematode Egg Counting**

This application reads high resolution scanner images and tracks and counts stained nematode eggs using OpenCV 3.1 and Python


Requirments
-----------
*Environment Setup*

* Download & Install `OpenCV 3.1.0 <http://opencv.org/downloads.html>`_ 
* Download & Install `Python 2.7 <https://www.python.org/downloads/>`_ 
* Using pip install  `numpy <https://www.scipy.org/scipylib/download.html>`_ and `matplotlib <https://matplotlib.org/>`_
* Copy cv2.pyd_ file from [OPENCV_LOCATION]/build/python/2.7/[x64 or x86]/ to [PYTHON_LOCATION]/Lib/site_packages/

It was tested on Windows and Mac OS X.

Usage
-----
Run ``python src/scanner_img_processing.py``


Steps involved
--------------
The code performs these following steps:

1. Read high resolution scanner image and split into 1024*1024*3 block and store them as a list of numpy arrays
2. It loops though each block and detects any eggs in that block and prints the count
3. Total egg count is printed along with the time taken for the script at the end 


Here are some of the snapshots
-------------------------------

.. image:: Images/snapshot_of_a_block.PNG


License
-------

This code is GNU GENERAL PUBLIC LICENSED.


Contributing
------------

If you have any suggestions or identified bugs please feel free to post them! 



