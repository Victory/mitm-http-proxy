import sys
from os.path import dirname, realpath
sys.path.append(dirname(dirname(realpath(__file__))))

import SimpleHTTPServer
import SocketServer
import os

from threading import Thread
from urllib2 import urlopen
from MitmHttpProxy import MitmHttpProxy
from time import sleep


def shutdown_thread(t):
    print "shutting down thread"
    t.shutdown()
    while t.isAlive():
        sleep(.1)
    print "done shutting down thread"


class ReusableTCP(SocketServer.TCPServer):
    allow_reuse_address = True


class Httpd(Thread):
    httpd = None

    def __init__(self):
        super(Httpd, self).__init__()

        self.PORT = 8000
        Handler = SimpleHTTPServer.SimpleHTTPRequestHandler
        self.httpd = ReusableTCP(("", self.PORT), Handler)
        self.httpd.timeout = 3
        print "serving at port", self.PORT

    def run(self):
        self.httpd.serve_forever()

    def shutdown(self):
        print "Shutting down httpd"
        self.httpd.shutdown()
        print "Done with httpd shutdown"

if __name__ == '__main__':
    os.chdir(dirname(dirname(realpath(__file__))) + "/html")

    inport = "8777"
    http_port = "8000"

    httpd = Httpd()
    httpd.start()

    cap = MitmHttpProxy(
        '127.0.0.1', int(inport),
        '127.0.0.1', int(http_port))
    print "Starting Cap"
    cap.start()
    print "Cap Running"
    print "Joining 2"
    cap.join(2)
    print "Done Joining"
    print "Opening"

    response = urlopen('http://127.0.0.1:' + inport)
    print "**From server**"
    response1 = response.read()
    print response1
    print "**Done reading**"

    response = urlopen('http://127.0.0.1:' + inport)
    print "from server 2"
    response2 = response.read()
    print response2
    print "Done reading 2"

    print "Shutting Down"
    shutdown_thread(cap)
    shutdown_thread(httpd)

    assert response1.find("INJECTED!")
    assert response2.find("INJECTED!")
