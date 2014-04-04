import sys
from os.path import dirname, realpath
sys.path.append(dirname(dirname(realpath(__file__))))

from time import sleep

import SimpleHTTPServer
import SocketServer

from selenium import webdriver
from threading import Thread

from MitmHttpProxy import MitmHttpProxy


BASEDIR = dirname(dirname(realpath(__file__)))
HOME = "file://" + BASEDIR + "/html"


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

    inport = "8777"
    http_port = "8000"

    httpd = Httpd()
    httpd.start()

    cap = MitmHttpProxy(
        '127.0.0.1', int(inport),
        '127.0.0.1', int(http_port))

    cap.start()
    cap.join(2)

    driver = webdriver.Firefox()

    def ijb(body):
        body = body.replace(
            "<body>",
            "<body><p id='injected'>INJECTED!</p>")
        return body

    cap.inject_body_function = ijb

    driver.get("http://127.0.0.1:" + inport + "/html/index.html")
    sleep(5)

    try:
        injected = driver.find_element_by_id('injected')
    except:
        injected = None

    driver.close()

    shutdown_thread(cap)
    shutdown_thread(httpd)

    assert injected
