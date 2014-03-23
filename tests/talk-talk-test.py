import socket
from threading import Thread
from time import sleep
from subprocess import Popen, PIPE, STDOUT


def shutdown_thread(t):
    print "shutting down"
    t.shutdown()
    while t.isAlive():
        sleep(.1)
    print "done shutting down"


def send_with_netcat(msg):
    nc = Popen(
        ['nc', '127.0.0.1', '8000'],
        stdin=PIPE,
        stdout=PIPE,
        stderr=STDOUT)

    result = nc.communicate(msg)
    return result


class Server(Thread):
    is_shutdown = False

    def __init__(self):
        super(Server, self).__init__()
        self.start_server()

    def start_server(self):
        self.server = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM)

        # "A socket is a 5 tuple (proto, local addr, local port,
        # remote addr, remote port).  SO_REUSEADDR just says that you
        # can reuse local addresses.  The 5 tuple still must be
        # unique!"
        self.server.setsockopt(
            socket.SOL_SOCKET,
            socket.SO_REUSEADDR,
            1)

        self.server = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM)

        # bind the socket
        self.server.bind(('127.0.0.1', 8000))
        self.server.listen(5)

    def shutdown(self):
        self.is_shutdown = True

    def run(self):
        while not self.is_shutdown:
            con, addr = self.server.accept()
            print "trying to recv", addr
            buf = con.recv(128)
            print "recved"
            if len(buf) > 0:
                print "from client --> ", buf

            print "shutting down con"
            con.shutdown(socket.SHUT_RDWR)
            print "closing con"
            con.close()
            print "done closing con"
            sleep(.1)

        print "running server shutdown"
        self.server.shutdown(socket.SHUT_RDWR)
        print "running server close"
        self.server.close()
        print "done closing"

if __name__ == '__main__':
    s = Server()
    s.start()
    send_with_netcat("None genuine without this seal!")
    shutdown_thread(s)
    sleep(5)
