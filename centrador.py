#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
la logica de este programa es de leer  coordenadas en pixel y convertilas en pasos de motor para llevar estar el blanco al centro de la imagen predefinido 
"""
import xmlrpclib
import time
import math

MOTORES_IP = "127.0.0.1"

elevation_controller = xmlrpclib.ServerProxy("http://" + MOTORES_IP + ":8001")
azimuth_controller = xmlrpclib.ServerProxy("http://" + MOTORES_IP + ":8000")


centroX = 325
centroY = 231 
radiuscentro = 5  # variable 
pixel = float(5.791) # esta variable es el numero de pixel que se mueven por cada paso de motor ,ver con cada cambio de resolucion de y relacion de motores

while True:

 X = input("entrar cordenadas x :  ") 
 Y = input("entrar cordenadas y :  ")

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

 print "New positon: %f %d" % (elevation_controller.position(), azimuth_controller.position())


     