import socket
import re

from time import sleep
from select import select
from threading import Thread


class CollectAllProxy(Thread):
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
        bufsize = 5
        eof_re = re.compile("\r\n\r\n")

        content = ""
        recved = clientsocket.recv(bufsize)
        while recved:
            print "*%s*" % recved
            content += recved
            if "Connection: close" in content and eof_re.search(content):
                break
            recved = clientsocket.recv(bufsize)

        clientsocket.close()
        print content

if __name__ == '__main__':
    cap = CollectAllProxy(
        '127.0.0.1', 8877,
        '127.0.0.1', 8000)
    cap.run()
