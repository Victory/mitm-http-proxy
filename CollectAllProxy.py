import socket
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

        # comes in locally
        self.incon = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM)

        self.incon.setsockopt(
            socket.SOL_SOCKET,
            socket.SO_REUSEADDR,
            1)

        self.incon = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM)

        # bind the socket
        self.incon.bind((self.inhost, self.inport))
        self.incon.listen(10)

        # outgoing socket (goes to http server)
        self.outcon = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM)

        self.outcon.setsockopt(
            socket.SOL_SOCKET,
            socket.SO_REUSEADDR,
            1)

        self.outcon = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM)

        # bind the socket
        self.outcon.bind((self.outhost, self.outport))
        self.outcon.listen(10)

        super(CollectAllProxy, self).__init__()

    def shutdown(self):
        self.is_shutdown = True

    def run(self):
        while 1:
            inrlist = self.into
            print "selecting"
            rready, wready, xready = select(inrlist, [], [], 5)
            print "done selecting"
            for self.inc in rready:
                incomming_content = ''
                cur_content = self.c.recv(1024)
                while cur_content:
                    print "cur content"
                    incomming_content += cur_content
                    cur_content = self.c.recv(1024)

                print "================= incomming"
                print incomming_content
                print "================= incomming"

        print "Nothing Ready"

if __name__ == '__main__':
    cap = CollectAllProxy(
        '127.0.0.1', 8877,
        '127.0.0.1', 8000)
    cap.run()
