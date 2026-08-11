#!/usr/bin/python3
import http.server
import socketserver
import json
import socket


WEB_PORT = 8000
BUFF_SIZE = 4096
NETIFY_HOST = '127.0.0.1'
NETIFY_PORT = 2100
NETIFY_CONNECT_TIMEOUT = 5


class MyHandler(http.server.BaseHTTPRequestHandler):

    def connect_netify(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        s.settimeout(NETIFY_CONNECT_TIMEOUT)
        s.connect((NETIFY_HOST, NETIFY_PORT))
        s.settimeout(None)
        print('Connected to netify agent')
        return s

    def stream_netify(self):
        try:
            s = self.connect_netify()
        except OSError as err:
            print(f'Could not connect to netify agent: {err}')
            return

        try:
            while True:
                data = s.recv(BUFF_SIZE)
                if not data:
                    break
                self.wfile.write(data)
        except OSError as err:
            print(f'Closing connection: {err}')
        finally:
            s.close()

    def do_GET(self):
        try:
            content_length = int(self.headers.get('Content-Length') or 0)
            if content_length:
                input_data = json.loads(self.rfile.read(content_length))
            else:
                input_data = {"Company": "Netcom Solutions"}
        except ValueError:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b'ERROR 400: Invalid request body')
            return

        print(input_data)

        if self.path == '/api/v1/dpi/traffic':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.stream_netify()
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'ERROR 404: Not found!')


class ThreadingHTTPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    daemon_threads = True
    allow_reuse_address = True


try:
    with ThreadingHTTPServer(("", WEB_PORT), MyHandler) as httpd:
        print(f"Starting http://0.0.0.0:{WEB_PORT}")
        httpd.serve_forever()
except KeyboardInterrupt:
    print("Stopping by Ctrl+C")
    httpd.server_close()
