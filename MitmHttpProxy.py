from CollectAllProxy import CollectAllProxy


class MitmHttpProxy(CollectAllProxy):
    inject_body_function = None

    def inject_body(self, response):
        ijb = self.inject_body_function
        if not hasattr(ijb, '__call__'):
            print "NOT CALLABLE"
            return response

        response.inject_body(ijb)
        return response
