import io
import socket
import sys
import datetime


class WSGIServer(object):

    address_family = socket.AF_INET
    # This is the default socket type for TCP/IP, AF_INET means IPv4
    socket_type = socket.SOCK_STREAM
    # SOCK_STREAM means a TCP socket
    request_queue_size = 1
    # The number of requests to queue up before refusing new connections
    
    # When working with web sockets in python (or any other language), you
    # need to specify two key parameters: the address family and the socket type.
    # AF_INET stands for "Address Family Internet" and is used to specify
    # the addressing format to use with the sockets. There are a few variations
    # of AF_INET for different address formats (IPv4, IPv6, etc.). IPv4 is the
    # most common format for internet address formats.
    
    # SOCK_STREAM defines the socket type, which determines the transport protocol
    # and communication characteristics. TCP (Transmission Control Protocol) is the most
    # common transport protocol used on the internet. It is a connection-oriented
    # protocol that provides reliable, ordered, and error-checked delivery of data.
    # SOCK_STREAM is used to create a TCP socket, which is the most common type of socket
    # used for web servers and clients. It allows for bidirectional communication
    # between the client and server, and it ensures that data is delivered in the correct
    # order and without errors. There are other socket types, such as SOCK_DGRAM, SOCK_RAW etc.
    # that are used for different purposes, but SOCK_STREAM is the most common type.
    
    # When combined AF_INET and SOCK_STREAM creates a TCP/IPv4 socket that uses the afforementioned
    # addressing format and transport protocol. It is suitable for protocols like HTTP.
    
    def __init__(self, server_address):
        # Create a listening socket
        self.listen_socket = listen_socket = socket.socket(
            self.address_family,
            self.socket_type
        )
        # The socket is created using the special variables created above.
        # The init method is used because the server is a class and the init method
        # is called when the class is instantiated. The server_address variable
        # is a tuple that contains the host and port number. listen_socket is the
        # socket object created with the .socket function, address family and
        # socket type variables.
        
        listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # This line sets the newly created socket to allow address reuse. This essentially
        # means that we are disabling the timeout behavior of the socket. Usually there is a 2 minute
        # timeout when you restart a server. This line allows the server to restart immediately again.
        # .setsockopt means set stock options.
        
        # SOL_SOCKET is a socket option that allows you to set options at the socket level.
        # SO_REUSEADDR is the specific option just mentioned (allow address reuse).
        # 1 is a boolean value that enables the option. 0 would disable it.
        
        listen_socket.bind(server_address)
        # .bind is a method that binds the listien_socket created above to the
        # server address. This a the IP and port tuple.
        listen_socket.listen(self.request_queue_size)
        # .listien is a method that tells the socket to listien for incomming connections.
        # It includes request queue size that is set to 1 for this test server.
        host, port = self.listen_socket.getsockname()[:2]
        # This grabs the host and port number from the listen_socket object.
        # .getsockname() returns a tuple of the host and port number.
        # The [:2] slice is used to get the first two elements of the tuple.
        self.server_name = socket.getfqdn(host)
        # .getfqdn() stands for get fully qualified domain name. It returns the domain name if 
        # one is available. If not, you will get the IP address of the server.
        self.server_port = port
        # Assign the port number to the server_port class variable.
        self.headers_set = []
        # This returns the headers sent by the client for framework compatability.

    def set_app(self, application):
        self.application = application
        # This essentially attaches the Django application to the server.
        # the application parameter is the Django WSGI application from
        # diy_web_server.wsgi, which processes HTTP requests according to your
        # Django URL configuration and views. This simple method is what
        # enables your custom server to host any WSGI-compliant web
        # application, not just Django. You could just as easily use it with
        # Flask, Pyramid, or any other WSGI-compatible framework.

    def serve_forever(self):
        listen_socket = self.listen_socket
        # First, the listien_socket is assigned to a local variable.
        while True:
            self.client_connection, client_address = listen_socket.accept()
            # while True means that the server will run indefinitely.
            # .accept() is a method that waits for a client to connect to the server.
            # It returns a tuple of the client connection and the client address.
            self.handle_one_request()
            # After a client connects, the server will handle one request and then
            # return to the while loop to wait for another client connection.
            # This is a blocking call, meaning that the server will wait for a client
            # to connect before continuing. This is a simple way to handle multiple
            # clients, but it is not the most efficient way. In a production server,
            # you would want to use threading or multiprocessing to handle multiple
            # clients at the same time.

    def handle_one_request(self):
        request_data = self.client_connection.recv(1024)
        # This line receives the request data from the client connection established in
        # the serve_forever function above. recv() is used with a parameter for 1024 bytes.
        # This reads upto 1024 bytes from the client connection socket.
        self.request_data = request_data = request_data.decode('utf-8')
        # decodes the bytes (request_data) to a UTF-8 string.
        print(''.join(
            f'< {line}\n' for line in request_data.splitlines()
        ))
        # This debugging output is particularly useful when learning how web
        # servers work or when troubleshooting issues with your WSGI application.
        # It shows the raw HTTP request data received from the client in the
        # terminal, which can help you understand how the server is
        # interpreting the request and what headers are being sent. "<" signifies
        # incoming data, while ">" signifies outgoing data.

        self.parse_request(request_data)
        # The decoded request data is passed to the parse_request class method.
        # This method breaks down the request data into its defined components.
        # These components are then used to construct the WSGI environment
        # dictionary that is passed to the WSGI application callable.
        env = self.get_environ()
        # Here I contruct the just mentioned WSGI environment dictionary.
        # Here is all the information that is passed to the WSGI application
        # callable. This includes the request method, path, server name,
        # server port, and other necessary information using the class method
        # get_environ().

        result = self.application(env, self.start_response)
        # This line starts the WSGI compatible application (in this case Django)
        # callable with the environment dictionary and the start_response
        # class method that is used to set the response status and headers.

        self.finish_response(result)
        # This contructs a HTTP response from the result returned by the WSGI
        # compatible application (Django) stored in result. This includes the
        # status code, headers and body returned by the application. Once this
        # is sent to the client, the connection is closed.
        # The finish_response method is responsible for sending the HTTP response
        # back to the client. It constructs the response headers and body,
        # encodes them to bytes, and sends them over the client connection.
        # Finally, it closes the client connection to free up resources.


    # Below are the class methods that are used in the above code.
    
    def parse_request(self, text):
        # The request_data is passed to this method as a decoded UTF-8 string.
        request_line = text.splitlines()[0]
        # This line splits the request data into lines and takes the first line
        # which contains the request line. The request line is the first line
        # of the HTTP request and contains the request method, path, and HTTP version.
        request_line = request_line.rstrip('\r\n')
        # This line removes the trailing carriage return and newline characters
        # from the request line. This is important because the request line
        # is a string and we want to remove any extra whitespace or formatting
        # characters that may have been added by the client or the server.
        
        # The request line is formatted as follows:
        (self.request_method,  # GET
         self.path,            # /hello
         self.request_version  # HTTP/1.1
         ) = request_line.split()

    def get_environ(self):
        env = {}
        # The following code snippet does not follow PEP8 conventions
        # but it's formatted the way it is for demonstration purposes
        # to emphasize the required variables and their values
        #
        # Required WSGI variables
        env['wsgi.version']      = (1, 0)
        env['wsgi.url_scheme']   = 'http'
        env['wsgi.input']        = io.StringIO(self.request_data)
        env['wsgi.errors']       = sys.stderr
        env['wsgi.multithread']  = False
        env['wsgi.multiprocess'] = False
        env['wsgi.run_once']     = False
        # Required CGI variables
        env['REQUEST_METHOD']    = self.request_method    # GET
        env['PATH_INFO']         = self.path              # /hello
        env['SERVER_NAME']       = self.server_name       # localhost
        env['SERVER_PORT']       = str(self.server_port)  # 8888
        return env

    def start_response(self, status, response_headers, exc_info=None):
        current_date = datetime.datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
        # This line gets the current date and time in UTC format.
        # The strftime method formats the date and time according to the
        # specified format string. The format string used here is the
        # RFC 1123 date format, which is the standard format for HTTP
        # date headers.
        
        # Add necessary server headers
        server_headers = [
            # set server date dynamically
            ('Date', f'${current_date}'),
            ('Server', 'WSGIServer 0.2'),
        ]
        self.headers_set = [status, response_headers + server_headers]
        # To adhere to WSGI specification the start_response must return
        # a 'write' callable. We simplicity's sake we'll ignore that detail
        # for now.
        # return self.finish_response

    def finish_response(self, result):
        try:
            status, response_headers = self.headers_set
            # Extract the status and response headers from the headers_set above.
            response = f'HTTP/1.1 {status}\r\n'
            # Creates the first line of the HTTP response with the version and
            # status code.
            for header in response_headers:
                response += '{0}: {1}\r\n'.format(*header)
                # Iterates through each header tuple (name, value) and formats them
                # as key-value pairs
            response += '\r\n'
            # This line adds a blank line to separate the headers from the body.
            # This is a standard HTTP response format.
            for data in result:
                response += data.decode('utf-8')
                # The result parameter is an iterable returned by the WSGI application
                # (Django). Each item is decoded to a UTF-8 string and added to the response.
            print(''.join(
                f'> {line}\n' for line in response.splitlines()
            ))
            # Another debugging output that shows the ">" outgoing HTTP response data
            # in the terminal. This is useful for understanding what the server
            # is sending back to the client and for troubleshooting issues with
            # the response.
            response_bytes = response.encode()
            # This line encodes the response string to bytes. This is necessary
            # because the client connection expects the response to be in bytes.
            self.client_connection.sendall(response_bytes)
            # .sendall() is a method that sends the response bytes to the client
            # connection.
        finally:
            self.client_connection.close()
            # This line closes the client connection. This is important because
            # it frees up resources and allows the server to handle new client
            # connections.

SERVER_ADDRESS = (HOST, PORT) = '', 8888
# The server address constants are defined here.


def make_server(server_address, application):
    server = WSGIServer(server_address)
    # This line creates a new WSGIServer object, passing in the server address
    # (a tuple containing host and port). This triggers the __init__ method code,
    # which sets up the socket, binds it to the address and prepares to listien for
    # incoming connections.
    server.set_app(application)
    # This calls the set_app class method to attach the WSGI application (in this case Django)
    # to the server, so the server knows what application should handle incoming requests.
    return server
# Returns the server instance so the caller can use it.


# The following code is used to run the server from the command line.
# It checks if the script is being run directly (not imported as a module)
# and if so, it creates a server instance and starts serving requests.
# This is a common pattern in Python scripts to allow for both
# standalone execution and importation as a module.
# The __name__ variable is a special built-in variable in Python that
# represents the name of the current module. When a Python script is run,
# the __name__ variable is set to '__main__'.
if __name__ == '__main__':
    if len(sys.argv) < 2:
        # This line checks if the script is being run with the correct number of arguments.
        # If not, it prints an error message and exits the script.
        # The sys.argv list contains the command-line arguments passed to the script.
        sys.exit('Provide a WSGI application object as module:callable')
    app_path = sys.argv[1]
    # This line gets the WSGI application path (path to Django) from the command line arguments.
    module, application = app_path.split(':')
    # This splits the path into the module and application name.
    module = __import__(module)
    # This line imports the module specified in the command line argument.
    # __import__ is a built-in function that imports a module by name.
    application = getattr(module, application)
    # This line gets the WSGI application callable from the imported module.
    # getattr is a built-in function that gets an attribute (in this case the
    # Django settings file) from an object (in this case the module).
    # The application callable is the entry point for the WSGI application.
    httpd = make_server(SERVER_ADDRESS, application)
    # The make_server function is called to create a new WSGIServer
    # instance, passing in the server address and the application specified above.
    print(f'WSGIServer: Serving HTTP on port {PORT} ...\n')
    httpd.serve_forever()
    # The serve_forever  class method is called to start the server and begin.