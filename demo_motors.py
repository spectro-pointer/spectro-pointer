import xmlrpclib
import time

MOTORES_IP = "127.0.0.1"

elevation_controller = xmlrpclib.ServerProxy("http://" + MOTORES_IP + ":8001")
azimuth_controller = xmlrpclib.ServerProxy("http://" + MOTORES_IP + ":8000")

print "Moving to the blue LED.."

elevation_controller.move_to(0.6812)
azimuth_controller.move_to(17490)

print "Done, current position:"
print "  Elevation: %s" % (elevation_controller.position())
print "  Azimuth: %s" % (azimuth_controller.position())
