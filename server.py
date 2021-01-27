#  coding: utf-8 
import socketserver

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(socketserver.BaseRequestHandler):
    
    def handle(self):
        self.data = self.request.recv(1024).strip().decode()
        print ("Got a request of: %s\n" % self.data)
        # self.request.sendall(bytearray("OK",'utf-8'))

        header = self.data.split('\n')
        request_line = header[0].split()
        method = request_line[0]
        uri = request_line[1]
        print(uri)

        response = ''
        if method != "GET":
            response = self.get_header(405,)
            self.request.sendall(response.encode())
        else:
            if uri[-1] == '/':
                uri += "index.html"
            
            
            try:
                file_path = open("www" + uri)
            except FileNotFoundError:
                response = self.get_header(404,)
                response += "404 Error"
                self.request.sendall(response.encode())
                return
            except IsADirectoryError:
                response = self.get_header(301,)
                response += f"Location: {uri}/\n\n"
                self.request.sendall(response.encode())
                return
            
            content = file_path.read()
            file_path.close()

            if uri[-4:] == '.css':
                response = self.get_header(200, "text/css")
            if (uri[-5:] == '.html' and response == ''):
                response = self.get_header(200, "text/html")

            response += content
            self.request.sendall(response.encode())

    def get_header(self, status_code, mime_type = "text/html"):
        header = "HTTP/1.1 "
        if status_code == 200:
            header += "200 OK\n"
        elif status_code == 301:
            header += "301 Moved Permanently\n"
        elif status_code == 404:
            header += "404 Not Found\n"
        elif status_code == 405:
            header += "405 Method Not Allowed\n"
        
        header += "Server: Simple Python Server\n"
        if status_code != 301:
            header += f"Content-Type: {mime_type}\n\n"

        return header 


if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
