#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
la logica de este programa es de leer  coordenadas en pixel y convertilas en pasos de motor para llevar estar el blanco al centro de la imagen predefinido 
"""
import xmlrpclib
import time
import math

def centrador(elevation_controller, azimuth_controller, X, Y):
    centroX = 325 
    centroY = 231 
    radiuscentro = 5  # variable 
    pixel = float(5.791) # esta variable es el numero de pixel que se mueven por cada paso de motor ,ver con cada cambio de resolucion de y relacion de motores
    if   X == centroX :
        print "X centrado"
    elif X > centroX :
        deltaX = X - centroX
        stepX = abs(deltaX * pixel) 
        stepX = "{0:.0f}".format(stepX) 
        stepX = int(stepX)
        print deltaX
        print stepX 
        print "derecha"
        azimuth_controller.move_right(stepX)
    elif X < centroX :
        deltaX = X - centroX
        stepX = abs(deltaX * pixel)
        stepX = "{0:.0f}".format(stepX) 
        stepX = int(stepX)
        print deltaX
        print stepX 
        print "isquierda"
        azimuth_controller.move_left(stepX)
    if Y == centroY :
        print "Y centrado"
    elif Y > centroY :
        deltaY = Y - centroY
        f = abs(deltaY * pixel)
        # f = "{0:.0f}".format(f) 
        f = int(f)
        print deltaY
        print  f 
        print " abajo"
        p = elevation_controller.position() + f*0.00015
        print p
        elevation_controller.move_to(p)
    elif Y < centroY :
        deltaY = Y - centroY
        f = abs(deltaY * pixel)
        print deltaY
        # f = "{0:.0f}".format(f) 
        f = int(f)
        print  f 
        print " arriba"
        p = elevation_controller.position() - f*0.00015
        print p
        elevation_controller.move_to(p)
    return elevation_controller.position(), azimuth_controller.position()

def pixel2Absolute(X, Y, absolute_Center_Azimuth, absolute_Center_Elevation):
    centroX = 325 
    centroY = 231 
    azimuthMax = 19200
    radiuscentro = 5  # variable 
    pixel = float(5.791) # esta variable es el numero de pixel que se mueven por cada paso de motor ,ver con cada cambio de resolucion de y relacion de motores
    if   X == centroX :
        stepX = 0
    elif X > centroX :
        deltaX = X - centroX
        stepX = abs(deltaX * pixel) 
        stepX = "{0:.0f}".format(stepX) 
        stepX = (-1) * int(stepX)
    elif X < centroX :
        deltaX = X - centroX
        stepX = abs(deltaX * pixel)
        stepX = "{0:.0f}".format(stepX) 
        stepX = int(stepX)
    if Y == centroY :
        p = 0.000000
    elif Y > centroY :
        deltaY = Y - centroY
        f = abs(deltaY * pixel)
        # f = "{0:.0f}".format(f) 
        f = int(f)
        p = f*0.00015
        
    elif Y < centroY :
        deltaY = Y - centroY
        f = abs(deltaY * pixel)
        # f = "{0:.0f}".format(f) 
        f = int(f)
        p = (-1) * f * 0.00015
    
    if (absolute_Center_Azimuth + stepX) < 0:
        return [(absolute_Center_Azimuth + stepX + azimuthMax) , (absolute_Center_Elevation + p)]
    else:
        return [(absolute_Center_Azimuth + stepX) , (absolute_Center_Elevation + p)]