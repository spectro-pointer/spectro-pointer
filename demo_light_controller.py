import xmlrpclib
import time

IP = "127.0.0.1"

controller = xmlrpclib.ServerProxy("http://" + IP + ":8003")

print "Getting..."
r = controller.get()
print "Done "  + str(len(r[0]))
