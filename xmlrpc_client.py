import xmlrpclib

s = xmlrpclib.ServerProxy('http://127.0.0.1:8000', allow_none = True)
print s.total_steps()
print s.position()
s.move(True, 400)
print s.position()
