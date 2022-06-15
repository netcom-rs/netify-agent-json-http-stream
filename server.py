#!/usr/bin/python3
import http.server
from logging import Handler
import socketserver
import json
import socket
from xmlrpc.client import ProtocolError


WEB_PORT = 8000
buff_size = 4096
#cs = False
NETIFY_HOST = ''
NETIFY_PORT = 2100 

class MyHandler(http.server.BaseHTTPRequestHandler):
    global do_rcv, cs, connect
    def connect():
        global s
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        s.connect((NETIFY_HOST, NETIFY_PORT))
        print('Connected to server')

    #connect()

    def do_rcv(self):
        global buff_size, cs
        cs = False
        connect()
        while True:
            try:
                data = s.recv(buff_size)
                self.wfile.write(data)
                if cs == True:
                    s.close()
                    break
                if not data:
                    s.close()
                    break
            except ProtocolError:
                print("Closing connection")
                cs = True
                break
            except KeyError:
                raise
            except BrokenPipeError:
                print("Closing connection")
                cs = True
                break
            except OSError:
                print("Closing connection")
                cs = True
                break
            except Exception as err:
                raise

                
    
    def do_GET(self):
        # - request -
        if self.headers['Content-Length'] != None:
            content_length = int(self.headers['Content-Length'])
            print('content_length:', content_length)
        else:
            content_length = 0
        
        if content_length:
            input_json = self.rfile.read(content_length)
            input_data = json.loads(input_json)
        else:
            input_data = '{"Company": "Netcom Solutions"}'
            
        print(input_data)
        
        if self.path == '/api/v1/dpi/traffic':
        
            # - response -
        
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
        
            do_rcv(self)
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'ERROR 404: Not found!')
            return





Handler = MyHandler


try:
    with socketserver.TCPServer(("", WEB_PORT), Handler) as httpd:
        print(f"Starting http://0.0.0.0:{WEB_PORT}")
        httpd.allow_reuse_address = True
        httpd.serve_forever()
except KeyboardInterrupt:
    print("Stopping by Ctrl+C")
    cs = True
    httpd.server_close()  # to resolve problem `OSError: [Errno 98] Address already in use`
    s.close() 
except Exception:
    print("Stopping by other exception")
    cs = True
    httpd.server_close()
