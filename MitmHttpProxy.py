from CollectAllProxy import CollectAllProxy


class MitmHttpProxy(CollectAllProxy):

    def inject_body(self, response):
        def inject_body(body):
            body = body.replace(
                "<body>",
                "<body><p id='injected'>INJECTED!</p>")
            return body

        response.inject_body(inject_body)
        return response
