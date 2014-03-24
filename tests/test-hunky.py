import sys
from os.path import dirname, realpath
sys.path.append(dirname(dirname(realpath(__file__))))

from urllib2 import urlopen
from CollectAllProxy import CollectAllProxy
from httplib import BadStatusLine
from time import sleep


def shutdown_thread(t):
    print "shutting down"
    t.shutdown()
    while t.isAlive():
        sleep(.1)
    print "done shutting down"


if __name__ == '__main__':
    cap = CollectAllProxy(
        '127.0.0.1', 8877,
        '127.0.0.1', 8000)
    print "Starting Cap"
    cap.start()
    print "Cap Running"
    print "Joining 2"
    cap.join(2)
    print "Done Joining"
    print "Opening"

    try:
        response = urlopen('http://127.0.0.1:8877')
        print "Reading..."
        response.read()
    except BadStatusLine, e:
        print "got the expected bad response"

    print "Done reading"

    print "Shutting Down"
    shutdown_thread(cap)
