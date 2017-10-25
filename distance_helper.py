# -*- coding: utf-8 -*-
"""
Created on Thu Oct 19 01:15:26 2017

@author: newho
"""

import numpy as np

def calculate_euclidean_distance(p1, p2):
    'Calculates the Euclidean Distance Between two points'
    return np.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)
print calculate_euclidean_distance([1, 1], [2, 6])