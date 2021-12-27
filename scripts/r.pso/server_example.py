from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
import threading
import queue
import time
from urllib.parse import parse_qs


class Handler(BaseHTTPRequestHandler):
    def __init__(self, request, client_address, server):
        self.queue = server.queue
        # self.queue = kwargs.pop("queue")
        super().__init__(request, client_address, server)

    def do_GET(self):
        action = "unknown"
        qd = "nav"
        if self.path == "/setup":
            self.queue.put(self.client_address)
            action = "returnSetup()"
        if self.path == "/particle":
            action = "returnParticle()"
            if not self.queue.empty():
                qd = self.queue.get()
            else:
                self.send_error(404, "no more particles")
                return
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        resp = "<html><head><title>Servera atbilde</title></head><body><h1>Atbilde</h1><p>{} {}</p></body></html>".format(qd, action)
        self.wfile.write(resp.encode())

    def do_POST(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        content_len = int(self.headers.get('Content-Length'))
        post_body = self.rfile.read(content_len)
        self.wfile.write("received post request:<br>{}".format(post_body))

class ThreadingSimpleServer(ThreadingMixIn, HTTPServer):
    pass


def run():
    q = queue.Queue()
    server = ThreadingSimpleServer(('0.0.0.0', 4444), Handler)
    server.queue = q
    q.put("viens")
    q.put("divi")
    server.serve_forever()


if __name__ == '__main__':
    run()
