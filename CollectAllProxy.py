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
            print "---\nCNT:", message, ":TNC\n----\n"

        reply = self.forward_message(clientsocket, message)

        self.send_response(clientsocket, reply)

        clientsocket.close()

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

        print "\nThe Reply:\n"
        print reply
        print "\n---end reply---\n"

        reply = reply.replace("Content-Length: 130", "Content-Length: 141")
        reply += "\nINJECTED!\n"

        return reply

    def adjust_content_length(self, reply):
        pass

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
