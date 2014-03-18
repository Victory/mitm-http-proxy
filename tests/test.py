import sys
from os.path import dirname, realpath
sys.path.append(dirname(dirname(realpath(__file__))))

import threading
import SimpleHTTPServer
import SocketServer
import socket

from time import sleep

from selenium import webdriver

import MitmHttpProxy

global more_requests
more_requests = True


class RunRequests(threading.Thread):
    is_shutdown = False
    delay = .01

    def __init__(self):
        super(RunRequests, self).__init__()

    def shutdown(self):
        soc = self.server.socket
        soc.shutdown(socket.SHUT_RDWR)
        soc.close()
        self.is_shutdown = True

    def run(self):
        Handler = SimpleHTTPServer.SimpleHTTPRequestHandler
        self.server = SocketServer.TCPServer(('127.0.0.1', 8000), Handler)

        while not self.is_shutdown:
            sleep(self.delay)
            print "handling request"
            try:
                self.server.handle_request()
            except Exception, e:
                print e
                print "Bailing from request handler"
                return

            print "request finished"

        print "Done Handling Request"


def run_server():
    print "Starting server"
    thread = RunRequests()
    thread.start()
    print "Server running"
    return thread


def kill_server(server):
    if server is None:
        print "Server already down"
        return
    print "Shutting down server"
    server.shutdown()
    print "Done shutting down server"


def run_proxy():
    ip = MitmHttpProxy.InjectionProxy(
        '127.0.0.1', 8877,
        '127.0.0.1', 8000)
    ip.start()
    print "Running Proxy"
    return ip


def kill_proxy(proxy):
    print "Killing Proxy"
    proxy.shutdown()


def run_selenium():
    proxy_addr = '127.0.0.1'
    proxy_port = '8877'

    profile = webdriver.FirefoxProfile()
    # manual proxy
    profile.set_preference("network.proxy.type", 1)
    profile.set_preference("network.proxy.http", proxy_addr)
    profile.set_preference("network.proxy.http_port", int(proxy_port))
    profile.set_preference("network.proxy.no_proxies_on", "")
    driver = webdriver.Firefox(firefox_profile=profile)
    kill_server(None)

    error = 0
    try:
        driver.get('http://127.0.0.1:8000/tests/test-pages/hello-world.html')
        elm = driver.find_element_by_id('injected')
        assert elm.text == 'injected'
    except Exception, e:
        print e
        error = 1
    finally:
        driver.quit()

    return error


if __name__ == '__main__':
    test_result = 1
    server = None
    proxy = None
    try:
        server = run_server()
        proxy = run_proxy()
        test_result = run_selenium()
    except Exception, e:
        print e
    finally:
        kill_server(server)
        kill_proxy(proxy)

    print "Done with test"

    exit(test_result)
