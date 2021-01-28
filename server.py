#  coding: utf-8 
import os, socketserver

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
        # print ("Got a request of:\n%s\n" % self.data)

        # if empty request, don't do anything
        if self.data:
            # split to get method and uri
            header = self.data.split('\n')
            request_line = header[0].split()
            method = request_line[0]
            self.uri = request_line[1]
        else:
            return

        response = ''
        if method != "GET":
            # status 405 for unsupported methods
            response = self.get_header(405,)
            self.request.sendall(response.encode())
        else:
            # append index.html for directories (assume xxx/ are all
            # directories)
            if self.uri[-1] == '/':
                self.uri += "index.html"

            # inteligently convert paths to absolute paths
            # Taken from Russel Dias from https://stackoverflow.com/a/5137509
            # on Jan 27, 2020
            root_dir = os.path.dirname(os.path.realpath(__file__))
            root_dir = os.path.join(root_dir, "www")
            uri_path = os.path.abspath(os.path.join(root_dir, self.uri[1:]))
            # check if uri_path is a subpath of root_dir, return 404 is uri is
            # not in www/, commonpath() returns longest common sub-path
            # Taken from Simon from https://stackoverflow.com/q/3812849 on
            # Jan 27, 2020
            if os.path.commonpath([root_dir, uri_path]) != root_dir:
                response = self.get_header(404)
                response += "<h1>404 Error</h1>"
                self.request.sendall(response.encode())
                return

            try:
                file_path = open(uri_path)
            # if file not found, return status 404
            except FileNotFoundError:
                response = self.get_header(404)
                response += "<h1>404 Error</h1>"
                self.request.sendall(response.encode())
                return
            # if uri is a directory but without '/', we redirect using status
            # 301
            except IsADirectoryError:
                response = self.get_header(301)
                self.request.sendall(response.encode())
                return
            # read file content and close file
            content = file_path.read()
            file_path.close()
            response = self.get_header(200)
            # append content to header and send
            response += content
            self.request.sendall(response.encode())


    def get_header(self, status_code):
        """
        Returns header based on status codes

        Parameters
        ----------
        status_code : int
            Status code in HTTP response

        Returns
        -------
        header : str
            Header to be sent to client in HTTP response
        """
        header = "HTTP/1.1 "
        if status_code == 200:
            header += "200 OK\n"
        elif status_code == 301:
            header += "301 Moved Permanently\n"
            # redirect to directory by appending '/'
            header += "Location: " + self.uri + "/\n\n"
        elif status_code == 404:
            header += "404 Not Found\n"
        elif status_code == 405:
            header += "405 Method Not Allowed\n"
        
        header += "Server: Simple Python Server\n"
        # CSS mime-type, defaults to html
        if self.uri[-4:] == ".css":
            header += "Content-Type: text/css\n\n"
        else:
            header += "Content-Type: text/html\n\n"

        return header 


if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
