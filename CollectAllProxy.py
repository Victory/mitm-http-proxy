import socket
from time import sleep
from select import select
from threading import Thread
from urllib2 import urlopen

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
        return


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



    def shutdown(self):
        self.is_shutdown = True

    def run(self):
        self.into.append(self.incon)
        while not self.is_shutdown:
            inrlist = self.into
            print "selecting", inrlist

            rready, wready, xready = select(inrlist, [], [])
            print "done selecting"
            for self.inc in rready:
                print "running rready"

                if self.incon == self.inc:
                    print "begin accept"
                    (clientsocket, addr) = self.inc.accept()
                    print "end accept"
                    print "recv from clientsocket"
                    content = clientsocket.recv(5)
                    new_content = True
                    while not self.is_shutdown and new_content:
                        print "client recv"
                        print clientsocket
                        rr, wr, xr = select([clientsocket], [], [], 5)
                        try:
                            new_content = rr[0].recv(5)
                        except:
                            self.into.shutdown()
                            self.into.close()

                        print "client end recv"
                        print new_content
                        if not new_content:
                            break
                        content += new_content
                    print content
                    print "Closing"
                    #clientsocket.shutdown(socket.SHUT_RDWR)
                    clientsocket.close()
                    print "done recv clientsocket"
                    break

                continue
                incomming_content = ''
                cur_content = self.inc.recv(1024)
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
