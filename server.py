import SocketServer
# coding: utf-8

# Copyright 2013 Abram Hindle, Eddie Antonio Santos, Tom Tran
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
import os

class MyWebServer(SocketServer.BaseRequestHandler):


    def handle(self):
        
        # self.request is the TCP socket connected to the client
        self.data = self.request.recv(1024).strip()
        print ("Got a request of: %s\n" % self.data)


        # Find the GET directory and set variables accordingly
        self.directory = 'www'+self.data.split()[1]
        

        # If the directory is not found, respond with 404 Not Found
        if not os.path.exists(self.directory) or self.data.split()[1][:3] == '/..':
            self.response_proto = 'HTTP/1.1'
            self.response_status = '404'
            self.response_status_text = 'Not Found'
            self.request.send('%s %s %s \n' % (self.response_proto, self.response_status, self.response_status_text))
            self.response_body = '<html><h1><body>404 Not Found</body></h1><html>'
            self.response_headers = "Content-Type: text/html;charset=utf-8\nContent-Length: %s\n" % (len(self.response_body))
            self.request.send(self.response_headers)
            self.request.send("\n")
            self.request.send(self.response_body)
            return


        # If path is a directory, respond with the index.html file
        if os.path.isdir(self.directory):
            # If directory does not end with a '/', redirect - 301 Moved Permanently
            if not self.directory[-1:] == '/':
                self.directory=self.data.split()[1]+'/'
                self.response_proto = 'HTTP/1.1'
                self.response_status = '301'
                self.response_status_text = 'Moved Permanently'
                self.request.send('%s %s %s \n' % (self.response_proto, self.response_status, self.response_status_text))
                self.response_body = '<HTML><HEAD><meta http-equiv="content-type" content="text/html;charset=utf-8">\n<TITLE>301 Moved</TITLE></HEAD><BODY>\n<H1>301 Moved</H1>\nThe document has moved\n<A HREF="%s">here</A>.\n</BODY></HTML>\n' % (self.directory)
                self.response_headers = "Location: %s\nContent-Type: text/html;charset=utf-8\nContent-Length: %s\n" % (self.directory,len(self.response_body))
                self.request.send(self.response_headers)
                self.request.send("\n")
                self.request.send(self.response_body)
                return
            # Respond with index.html when client GET directory
            self.directory+='index.html'
        

        # Respond with the correct MIME type
        if self.directory[-5:] == '.html':
            self.mimetype = 'text/html;charset=utf-8'
        if self.directory[-4:] == '.css':
            self.mimetype = 'text/css'


        # Prepare the response header                    
        self.response_proto = 'HTTP/1.1'
        self.response_status = '200'
        self.response_status_text = 'OK'
        self.request.send('%s %s %s \n' % (self.response_proto, self.response_status, self.response_status_text))

        
        # Prepare to send the response file
        self.file_pointer = open(self.directory)
        try:
            self.response_body = self.file_pointer.read()
            self.response_headers = "Content-Type: %s\nContent-Length: %s\n" % (self.mimetype, len(self.response_body))
            self.request.send(self.response_headers)
            self.request.send("\n")
            self.request.send(self.response_body)
        finally:
            self.file_pointer.close()



if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    SocketServer.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = SocketServer.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
