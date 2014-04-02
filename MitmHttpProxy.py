from CollectAllProxy import CollectAllProxy


class MitmHttpProxy(CollectAllProxy):

    def inject_body(self, response):
        def inject_body(body):
            body += "INJECTED!"
            return body

        response.inject_body(inject_body)
        return response
