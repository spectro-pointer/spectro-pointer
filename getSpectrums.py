# -*- coding: utf-8 -*-
"""
Created on Sun Dec 17 19:55:21 2017

@author: newho
"""

import numpy as np
import glob
from ipywidgets import interact, interactive, fixed, interact_manual
import ipywidgets as widgets
import matplotlib.pyplot as plt

files = glob.glob('C:/Users/newho/Documents/spectro-pointer/captures/*/*Individual_Lights/*/*.txt')
scores = np.loadtxt(files[0])
xvals = scores[:,0]
a = np.empty([scores.shape[0], len(files)])
for i, file in enumerate(files):
    scores = np.loadtxt(file)
    a[:, i] = scores[:, 1]
def plotter(index, xvals, a):
    plt.plot(xvals, a[:, index])
index_num = 0
interact(plotter, index = index_num, xvals = xvals, a = a)