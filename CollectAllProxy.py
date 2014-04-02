import socket
import re

from time import sleep
from select import select
from threading import Thread

from StringIO import StringIO
from httplib import HTTPResponse


class StringySocket(StringIO):
    def makefile(self, *args, **kw):
        """
        Used to mock set 'rb' flags etc...
        """
        return self


class StringyHttpResponse(object):
    """
    The last thing we need is a nother socket to deal with, lets deal
    with the reply as a string
    """
    body = None
    headers = None

    def __init__(self, content):
        ss = StringySocket(content)
        response = HTTPResponse(ss)
        response.begin()

        self.response = response

    def get_content_length(self):
        return len(self.get_body())

    def get_header_string(self, code=200):
        str_headers = [h[0] + ": " + str(h[1]) for h in self.get_headers()]
        if code == 200:
            status_line = "HTTP/1.0 200 OK\r\n"

        return status_line + "\r\n".join(str_headers)

    def set_header(self, header_name, value):
        header = header_name.lower()
        val = (header, value)
        for ii, h in enumerate(self.get_headers()):
            if h[0] == header:
                self.headers[ii] = val
                break

        self.headers.append(val)

        return self.headers

    def get_header(self, header_name):
        header = header_name.lower()
        for h in self.get_headers():
            if h[0].lower() == header:
                return h
        return None

    def get_headers(self):
        if not self.headers:
            self.headers = self.response.getheaders()
        return self.headers

    def get_body(self):
        if not self.body:
            self.body = self.response.read()
        return self.body

    def build_response(self):
        return self.get_header_string() + "\r\n" + self.get_body()


class CollectAllProxy(Thread):
    """
    Collects all of an incoming request, before modifying content and
    forwarding
    """

    into = []
    outof = []
    inchannel = {}
    outchannel = {}
    is_shutdown = False

    def __init__(self,
                 inhost, inport,
                 outhost, outport):
        self.inhost = inhost
        self.inport = inport
        self.outhost = outhost
        self.outport = outport

        super(CollectAllProxy, self).__init__()

        self.incon = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM)

        self.incon.setsockopt(
            socket.SOL_SOCKET,
            socket.SO_REUSEADDR,
            1)

        # bind the socket
        self.incon.bind((self.inhost, self.inport))
        self.incon.listen(10)

    def shutdown(self):
        print "shutting down"
        self.is_shutdown = True

    def run(self):
        self.into.append(self.incon)
        while not self.is_shutdown:
            sleep(.1)
            print "selecting"
            rready, wready, xready = select(self.into, [], [], 1)
            print "done selecting"
            for self.inc in rready:
                print "running rready"

                if self.incon == self.inc:
                    print "begin accept"
                    (clientsocket, addr) = self.inc.accept()
                    self.handle_accept(clientsocket, addr)
        self.incon.close()

    def handle_accept(self, clientsocket, addr):
        # set low so we have to iter over recv
        bufsize = 50
        eof_re = re.compile("\r\n\r\n")

        message = ""
        recved = clientsocket.recv(bufsize)
        while recved:
            print "*%s*" % recved
            message += recved
            if eof_re.search(message):
                break
            recved = clientsocket.recv(bufsize)

        reply = self.forward_message(clientsocket, message)

        self.send_response(clientsocket, reply)

        clientsocket.close()

    def inject_headers(self, response):
        return response

    def inject_body(self, response):
        return response

    def forward_message(self, clientsocket, message):
        out = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM)

        out.connect((self.outhost, self.outport))

        out.send(message)

        reply = ""
        newContent = True
        buffsize = 50
        while newContent:
            sleep(.01)
            newContent = out.recv(buffsize)
            if not newContent:
                break
            reply += newContent

        response = StringyHttpResponse(reply)

        response = self.inject_body(response)
        response = self.inject_headers(response)
        response = self.adjust_content_length(response)

        print "\nbuild_response:\n"
        print response.build_response()
        print "\n---end build_response ---\n"

        return response.build_response()

    def adjust_content_length(self, response):
        content_length = response.get_content_length()
        response.set_header("content-length", content_length)
        return response

    def send_response(self, clientsocket, http):
        print "\n--- ready to send ---\n"
        print http
        print "\n--- done sending ---\n"
        clientsocket.send(http)


if __name__ == '__main__':
    cap = CollectAllProxy(
        '127.0.0.1', 8877,
        '127.0.0.1', 8000)
    cap.run()
