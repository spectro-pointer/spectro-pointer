import xmlrpclib
import time

class _Getch:
    """Gets a single character from standard input.  Does not echo to the
screen."""
    def __init__(self):
        try:
            self.impl = _GetchWindows()
        except ImportError:
            self.impl = _GetchUnix()

    def __call__(self): return self.impl()


class _GetchUnix:
    def __init__(self):
        import tty, sys

    def __call__(self):
        import sys, tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch


class _GetchWindows:
    def __init__(self):
        import msvcrt

    def __call__(self):
        import msvcrt
        return msvcrt.getch()

MOTORES_IP = "127.0.0.1"

elevation_controller = xmlrpclib.ServerProxy("http://" + MOTORES_IP + ":8001")
azimuth_controller = xmlrpclib.ServerProxy("http://" + MOTORES_IP + ":8000")

getch = _Getch()
while True:
  c = getch()
  if c == 'w':
    p = elevation_controller.position() - 0.00015
    elevation_controller.move_to(p)
  elif c == 's':
    p = elevation_controller.position() + 0.00015
    elevation_controller.move_to(p)
  elif c == 'a':
    azimuth_controller.move_left(5)
  elif c == 'd':
    azimuth_controller.move_right(5)
  else:
    print 'Unknown command!'
    exit()

  print "New positon: %f %d" % (elevation_controller.position(), azimuth_controller.position())
