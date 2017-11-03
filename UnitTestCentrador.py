# -*- coding: utf-8 -*-
"""
Created on Fri Nov  3 11:44:01 2017
Unit Tests
@author: newho
"""

import unittest
import centrador_test
 
class TestCentrador(unittest.TestCase):
 
    def setUp(self):
        pass
    def Pixel2AbsoluteTest(self):
        self.assertEqual(centrador_test.pixel2Absolute(400,600,0,0.669583), [18829, 0.9110830000000001])
 
if __name__ == '__main__':
    unittest.main()