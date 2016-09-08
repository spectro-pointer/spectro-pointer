import xmlrpclib
import time

MOTORES_IP = '127.0.0.1'

elevation_controller = xmlrpclib.ServerProxy('http://' + MOTORES_IP + ':8001')
elevation_controller.move_to(0.60)

azimuth_controller = xmlrpclib.ServerProxy('http://' + MOTORES_IP + ':8000')
position = azimuth_controller.position()
print 'Current position: ' + str(position)

azimuth_controller.move(True, 1000)
time.sleep(5.0)

azimuth_controller.move_to(position)
