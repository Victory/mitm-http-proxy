import sys
from os.path import dirname, realpath
sys.path.append(dirname(dirname(realpath(__file__))))

from urllib2 import urlopen
from CollectAllProxy import CollectAllProxy
from httplib import BadStatusLine
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
        pass # we know we are not returning valid http now
    print "Done reading"

    print "Shutting Down"
    cap.shutdown()
