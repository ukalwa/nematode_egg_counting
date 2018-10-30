""" Tests for validating utilties module methods. """
import os
import unittest

from nose.tools import raises, assert_raises, ok_
import cv2

from src.utilities import validate_file, read_image
import src.utilities as util


class TestUtilities(unittest.TestCase):
    """
    Tests for Utilities module
    """
    @classmethod
    def setUpClass(cls):
        cls.test_file_name = os.path.abspath(__file__)
        print("Test File Name: ", cls.test_file_name)

        cls.img_dir = os.path.join(os.path.dirname(cls.test_file_name),
        "..", "Images")
        cls.img_file = os.path.join(cls.img_dir, "test_image.jpg")
        print(os.path.isdir(cls.img_dir), os.path.isfile(cls.img_file))
        cls.img = cv2.imread(cls.img_file)

        cls.small_img_file = cv2.imread(os.path.join(cls.img_dir, "Picture1.jpg"))
        cls.corrupted_img_file = os.path.join(cls.img_dir, "config.jpg")
        print(os.path.isdir(cls.img_dir), os.path.isfile(cls.corrupted_img_file))

    def test_img_read(self):
        # Test empty filename
        assert_raises(FileNotFoundError, read_image, "")
        # Test filename with unsupported extension
        assert_raises(FileNotFoundError, read_image,self.test_file_name)
        # Test directory
        assert_raises(FileNotFoundError, read_image, self.img_dir)
        # Test corrupted filename
        assert_raises(IOError, read_image, self.corrupted_img_file)
        # Test valid filename
        ok_(read_image(self.img_file).all() == self.img.all())

    def test_split(self):
        assert_raises(ValueError, util.split_image, self.small_img_file, (1024,1024))

    def test_rect(self):
        ok_(util.cvt_rect((12,17,98,104))==(12,17,110,121)) 

if __name__ == "__main__":
    unittest.main()
