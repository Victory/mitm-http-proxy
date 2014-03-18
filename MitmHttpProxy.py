import socket
from time import sleep
from select import select
from threading import Thread


class ForwardTo(object):

    def __init__(self):
        """ create a forwarding inet, stream connection """

        self.con = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM)

    def start(self, hostname, port):
        try:
            self.con.connect((hostname, int(port)))
            self.con.settimeout(5)
            return self.con
        except Exception, exc:
            print "Could Not Connect to", hostname, port
            print exc
            return False


class InjectionProxy(Thread):

    incomming = []
    channel = {}
    is_shutdown = False

    def __init__(self,
                 host, port,
                 outgoing_host, outgoing_port,
                 delay=0.01, buffer_size=4096):
        self.host = host
        self.port = port
        self.outgoing_host = outgoing_host
        self.outgoing_port = outgoing_port

        self.delay = delay
        self.buffer_size = buffer_size
        self.con = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM)

        # set reusable socket to true
        self.con.setsockopt(
            socket.SOL_SOCKET,
            socket.SO_REUSEADDR,
            1)

        # bind the socket
        self.con.bind((host, port))

        # make the socket accept connections, with max backlog
        self.con.listen(10)

        super(InjectionProxy, self).__init__()

    def shutdown(self):
        self.is_shutdown = True

    def run(self):
        self.incomming.append(self.con)
        while not self.is_shutdown:
            sleep(self.delay)
            print "running while 1"

            # each incoming gets its a new wlist and xlist
            rlist = self.incomming
            print "selecting"
            rready, wready, xready = select(rlist, [], [], 5)
            print "done selecting", rready
            # for all the reading connections
            for self.c in rready:
                print "in for rready"

                # this is the current reading connection
                if self.c == self.con:
                    # do something with accepted content
                    self.run_accept()
                    break

                # read buffer_size worth of content, if we can't its
                # because of timeout, close or shutdown and we should
                # break out of the loop
                try:
                    self.content = self.c.recv(self.buffer_size)
                except socket.error:
                    break

                # close if there is no data or continue to read
                if len(self.content) == 0:
                    self.run_close()
                else:
                    self.run_recv(self.c)
                    pass

        for soc in self.incomming:
            print "closing", soc
            self.c = soc
            soc.shutdown(socket.SHUT_RDWR)
            soc.close()
            self.incomming.remove(soc)

        print "Done Closing", self.incomming, self.channel

    def run_accept(self):
        forward = ForwardTo().start(self.outgoing_host, self.outgoing_port)
        clientsock, clientaddr = self.con.accept()
        if forward:
            self.incomming.append(clientsock)
            self.incomming.append(forward)
            self.channel[clientsock] = forward
            self.channel[forward] = clientsock
        else:
            print "Cannot connect to", clientaddr
            clientsock.shutdown(socket.SHUT_RDWR)
            clientsock.close()

    def run_close(self):
        #remove objects from input_list
        self.incomming.remove(self.c)
        self.incomming.remove(self.channel[self.c])
        out = self.channel[self.c]

        # close the connection with client
        self.channel[out].close()  # equivalent to do self.s.close()
        # close the connection with remote server
        self.channel[self.c].close()
        # delete both objects from channel dict
        del self.channel[out]
        del self.channel[self.c]

    def run_recv(self, received):
        content = self.run_injection(received)
        self.channel[self.c].send(content)

    def run_injection(self, received):
        peer = self.c.getpeername()
        content = self.content
        return content

        is_incomming = (peer[0], peer[1]) == \
            (self.outgoing_host, self.outgoing_port)

        if is_incomming:
            content = content.replace(
                '<body>',
                '<body><p id="injected">injected</p>')
        else:
            replace = "GET http://" + \
            self.outgoing_host + ":" + str(self.outgoing_port)
            content = content.replace(replace, "GET ")

        return content

if __name__ == '__main__':
    print "starting proxy"
    ip = InjectionProxy(
        '127.0.0.1', 8877,
        '127.0.0.1', 8000)

    try:
        ip.run_loop()
    except KeyboardInterrupt:
        print "Closing server..."
        exit(1)
