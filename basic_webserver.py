import io
import socket
import sys


class WSGIServer(object):

    address_family = socket.AF_INET
    # This is the default socket type for TCP/IP, AF_INET means IPv4
    socket_type = socket.SOCK_STREAM
    # SOCK_STREAN means a TCP socket
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
        
        # Bind
        listen_socket.bind(server_address)
        # Activate
        listen_socket.listen(self.request_queue_size)
        # Get server host name and port
        host, port = self.listen_socket.getsockname()[:2]
        self.server_name = socket.getfqdn(host)
        self.server_port = port
        # Return headers set by Web framework/Web application
        self.headers_set = []

    def set_app(self, application):
        self.application = application

    def serve_forever(self):
        listen_socket = self.listen_socket
        while True:
            # New client connection
            self.client_connection, client_address = listen_socket.accept()
            # Handle one request and close the client connection. Then
            # loop over to wait for another client connection
            self.handle_one_request()

    def handle_one_request(self):
        request_data = self.client_connection.recv(1024)
        self.request_data = request_data = request_data.decode('utf-8')
        # Print formatted request data a la 'curl -v'
        print(''.join(
            f'< {line}\n' for line in request_data.splitlines()
        ))

        self.parse_request(request_data)

        # Construct environment dictionary using request data
        env = self.get_environ()

        # It's time to call our application callable and get
        # back a result that will become HTTP response body
        result = self.application(env, self.start_response)

        # Construct a response and send it back to the client
        self.finish_response(result)

    def parse_request(self, text):
        request_line = text.splitlines()[0]
        request_line = request_line.rstrip('\r\n')
        # Break down the request line into components
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
        # Add necessary server headers
        server_headers = [
            ('Date', 'Mon, 15 Jul 2019 5:54:48 GMT'),
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
            response = f'HTTP/1.1 {status}\r\n'
            for header in response_headers:
                response += '{0}: {1}\r\n'.format(*header)
            response += '\r\n'
            for data in result:
                response += data.decode('utf-8')
            # Print formatted response data a la 'curl -v'
            print(''.join(
                f'> {line}\n' for line in response.splitlines()
            ))
            response_bytes = response.encode()
            self.client_connection.sendall(response_bytes)
        finally:
            self.client_connection.close()


SERVER_ADDRESS = (HOST, PORT) = '', 8888


def make_server(server_address, application):
    server = WSGIServer(server_address)
    server.set_app(application)
    return server


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit('Provide a WSGI application object as module:callable')
    app_path = sys.argv[1]
    module, application = app_path.split(':')
    module = __import__(module)
    application = getattr(module, application)
    httpd = make_server(SERVER_ADDRESS, application)
    print(f'WSGIServer: Serving HTTP on port {PORT} ...\n')
    httpd.serve_forever()