import sys
from os.path import dirname, realpath
sys.path.append(dirname(dirname(realpath(__file__))))

import unittest

from CollectAllProxy import StringyHttpResponse


class TestStringHttpResponse(unittest.TestCase):
    def setUp(self):
        self.content = """HTTP/1.0 200 OK
Server: SimpleHTTP/0.6 Python/2.7.3
Date: Mon, 31 Mar 2014 23:20:46 GMT
Content-type: text/html
Content-Length: 130
Last-Modified: Sat, 29 Mar 2014 17:00:03 GMT

<!DOCTYPE HTML>
<html>
  <head>
    <title>A Test Page</title>
  </head>
  <body>
    <p>Hi I am the Index!</p>
  </body>
</html>
"""
        self.response = StringyHttpResponse(self.content)

    def test_get_content_length(self):
        expected = 130
        actual = self.response.get_content_length()
        self.assertTrue(actual == expected)

    def test_get_header_string_has_200_OK(self):
        self.assertTrue("200 OK" in self.response.get_header_string())

    def test_get_header(self):
        expected = ('content-length', '130')
        actual = self.response.get_header('content-length')
        self.assertTrue(expected == actual)

    def test_set_content_length_header(self):
        self.response.set_header('content-length', '150')
        expected = ('content-length', '150')
        actual = self.response.get_header('content-length')
        self.assertTrue(expected == actual)

        header_string = self.response.get_header_string()
        expected = 'content-length: 150'
        self.assertTrue(expected in header_string)

if __name__ == '__main__':
    unittest.main()
