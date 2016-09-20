import xmlrpclib
import time

MOTORES_IP = "127.0.0.1"

elevation_controller = xmlrpclib.ServerProxy("http://" + MOTORES_IP + ":8001")
elevation_controller.move_to(0.60)

azimuth_controller = xmlrpclib.ServerProxy("http://" + MOTORES_IP + ":8000")

position = azimuth_controller.position()
print "Current position: " + str(position)

print "Moving left..."
azimuth_controller.move(True, 1000)
print "Done, currently at position = " + str(azimuth_controller.position())
time.sleep(5.0)

print "Moving back to inital position (should go right)..."
azimuth_controller.move_to(position)
print "Done, currently at position = " + str(azimuth_controller.position())
time.sleep(5.0)

print "Moving right..."
azimuth_controller.move(False, 1000)
print "Done, currently at position = " + str(azimuth_controller.position())
time.sleep(5.0)

print "Moving back to inital position (should go left)..."
azimuth_controller.move_to(position)
print "Done, currently at position = " + str(azimuth_controller.position())
time.sleep(5.0)
