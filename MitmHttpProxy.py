import SocketServer
import SimpleHTTPServer

from threading import Thread

from CollectAllProxy import CollectAllProxy


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


class MitmHttpProxy(CollectAllProxy):
    inject_body_function = None
    inject_body_condition_function = None

    def inject_body(self, response):
        ijb = self.inject_body_function
        ijc = self.inject_body_condition_function

        if not hasattr(ijb, '__call__'):
            return response

        if hasattr(ijc, '__call__'):
            if not inject_body_condition_function(response):
                return response

        response.inject_body(ijb)
        return response
