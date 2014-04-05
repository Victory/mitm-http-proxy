import sys
import os
from os.path import dirname, realpath
sys.path.append(dirname(dirname(realpath(__file__))))

from time import sleep

from selenium import webdriver

from MitmHttpProxy import MitmHttpProxy, Httpd, shutdown_thread

on_error_handler = """
<script type="text/javascript">
window.addEventListener('error', function (evt) {
  // this is only for proof of concept, its possible you
  // wont even have a <body> element when an error happens
  var body = document.getElementsByTagName('body')[0];
  var injected = document.createElement('p');
  injected.setAttribute('id', 'injected');
  injected.textContent = "INJECTED!";
  body.appendChild(injected);
});
</script>
"""


if __name__ == '__main__':
    os.chdir(dirname(dirname(realpath(__file__))) + "/html")

    inport = "8777"
    http_port = "8000"

    httpd = Httpd()
    httpd.start()

    cap = MitmHttpProxy(
        '127.0.0.1', int(inport),
        '127.0.0.1', int(http_port))

    cap.start()
    cap.join(2)

    driver = webdriver.Firefox()

    def ijb(body):
        body = body.replace(
            "<head>",
            "<head>" + on_error_handler)
        return body

    cap.inject_body_function = ijb

    driver.get("http://127.0.0.1:" + inport + "/has-javascript-error.html")
    sleep(5)

    try:
        injected = driver.find_element_by_id('injected')
    except:
        injected = None

    driver.close()

    shutdown_thread(cap)
    shutdown_thread(httpd)

    assert injected
