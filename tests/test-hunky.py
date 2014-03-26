import sys
from os.path import dirname, realpath
sys.path.append(dirname(dirname(realpath(__file__))))

from urllib2 import urlopen
from CollectAllProxy import CollectAllProxy
#from httplib import BadStatusLine
from time import sleep


def shutdown_thread(t):
    print "shutting down"
    t.shutdown()
    while t.isAlive():
        sleep(.1)
    print "done shutting down"


if __name__ == '__main__':

    inport = "8777"
    cap = CollectAllProxy(
        '127.0.0.1', int(inport),
        '127.0.0.1', 8000)
    print "Starting Cap"
    cap.start()
    print "Cap Running"
    print "Joining 2"
    cap.join(2)
    print "Done Joining"
    print "Opening"

    response = urlopen('http://127.0.0.1:' + inport)
    print "from server"
    print response.read()
    print "Done reading"

    print "Shutting Down"
    shutdown_thread(cap)
