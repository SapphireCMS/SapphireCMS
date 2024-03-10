import json
import logging
import os, sys, select, socket
import ssl
import threading
import time
import traceback

from .request import Request
from .response import Response
from sapphirecms.logs import server_logger, socket_logger, client_logger, worker_logger
    
class Socket:
    """
    Represents a socket connection to a client.

    Args:
        socket (socket): The socket object.
        address (str): The address of the client.

    Attributes:
        socket (socket): The socket object.
        address (str): The address of the client.
        buffer (str): The buffer for receiving data from the client.
        logger (Logger): The logger object for logging socket events.

    """

    def __init__(self, host, port, buffer_size, keyfile=None, certfile=None, cert_reqs=ssl.CERT_NONE, ca_certs=None, suppress_ragged_eofs=True, ciphers=None):
        self.host = host
        self.port = port
        self.buffer_size = buffer_size
        self._socket = None
        self.https = certfile and keyfile
        if self.https:
            self.certfile = certfile
            self.keyfile = keyfile
            self.cert_reqs = cert_reqs
            self.ca_certs = ca_certs
            self.suppress_ragged_eofs = suppress_ragged_eofs
            self.ciphers = ciphers
        self.id = None
        
    def fileno(self):
        """
        Returns the file descriptor of the socket.
        """
        return self._socket.fileno()
        
    def send(self, data):
        """
        Sends data to the client.
        """
        logger = socket_logger(self.id)
        if not self._socket:
            logger.warning("Socket connection not started.")
            return
        logger.info("Sending response to %s:%s..." % (self.client_socket.getsockname()[0], self.client_socket.getsockname()[1]))
        self.client_socket.send(data)
    
    def get_client(self):
        """
        Returns the next client connection.
        """
        return Client(*self._socket.accept())
        
    
    def start(self, override=False):
        """
        Starts the socket connection.
        """
        if self._socket and not override:
            logger = socket_logger(self.id)
            logger.warning("Socket connection already started.")
            return
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if self.https:
            self._socket = ssl.wrap_socket(self._socket, server_side=True, certfile=self.certfile, keyfile=self.keyfile, cert_reqs=self.cert_reqs, ca_certs=self.ca_certs, suppress_ragged_eofs=self.suppress_ragged_eofs, ciphers=self.ciphers)
        self._socket.bind((self.host, self.port))
        self.id = self._socket.fileno()
    
    def listen(self):
        """
        Listens for incoming connections.
        """
        if not self._socket:
            logger.warning("Socket connection not started.")
            return
        logger = socket_logger(self.id)
        logger.info("Listening for incoming connections <%s:%s>..." % (self.host, self.port))
        self._socket.listen()
        
    def disconnect(self):
        """
        Disconnects the socket connection.
        """
        if not self._socket:
            logger = socket_logger(self.id)
            logger.warning("Socket connection not started.")
            return
        self._socket.disconnect()
    
    def close(self):
        """
        Closes the socket connection.
        """
        if not self._socket:
            logger = socket_logger(self.id)
            logger.warning("Socket connection not started.")
            return
        self._socket.close()

class Client:
    def __init__(self, client_socket, address):
        self.client_socket = client_socket
        self.client_socket.setblocking(False)
        self.address = address
        self.buffer_size = 1024

    def receive(self):
        """
        Receives data from the client.
        """
        logger = client_logger(self.address)
        blocks = []
        while select.select([self.client_socket], [], [], 0.2)[0]:
            blocks.append(self.client_socket.recv(self.buffer_size))
        self.client_socket = self.client_socket
        return b"".join(blocks).decode()
    
    def disconnect(self):
        """
        Disconnects the client socket.
        """
        logger = client_logger(self.address)
        self.client_socket.close()
        logger.info("Disconnect")
        print("")
        del self.client_socket
        del self.address
        del self
        
    def send(self, data):
        """
        Sends data to the client.
        """
        logger = client_logger(self.address)
        logger.info("Sending response to client...")
        self.client_socket.send(data)

class Server:
    """
    Represents a server that listens for incoming connections and handles client requests.

    Args:
        host (str): The host address to bind the server socket to.
        port (int): The port number to bind the server socket to.
        max_connections (int): The maximum number of simultaneous connections allowed.
        max_buffer_size (int): The maximum size of the receive buffer for each client connection.
        router (Router): The router object responsible for handling client requests.

    Attributes:
        host (str): The host address to bind the server socket to.
        port (int): The port number to bind the server socket to.
        max_connections (int): The maximum number of simultaneous connections allowed.
        max_buffer_size (int): The maximum size of the receive buffer for each client connection.
        server_socket (socket): The server socket object.
        router (Router): The router object responsible for handling client requests.
        clients (list): A list of connected client sockets.
        logger (Logger): The logger object for logging server events.

    """

    def __init__(self, max_connections, router, auto_reload=False, debug=False, secret_key=None):
        self.max_connections = max_connections
        self.router = router
        self.auto_reload = auto_reload
        self.debug = debug if sys.argv[0] != "prod" else False
        
        self.logger = server_logger()
        self.logger.info("Server initialized.")
        
        self.secret_key = secret_key
    
    def start(self, sockets: list):
        """
        Starts the server.
        """
        self.logger.info("Starting Server")
        entrypoints = []
        for sock in sockets:
            sock.start()
            if sock.host != "0.0.0.0":
                entrypoints.append((f"http{'s' if sock.https else ''}://{sock.host}:{sock.port}/", {sock.id}))
            else:
                interfaces = [f"http{'s' if sock.https else ''}://{ip}:{sock.port}/" for ip in [ip for ip in socket.gethostbyname_ex(socket.gethostname())[2]]]
                interfaces.append(f"http{'s' if sock.https else ''}://{socket.gethostname()}:{sock.port}/")
                interfaces.append(f"http{'s' if sock.https else ''}://localhost:{sock.port}/")
                [entrypoints.append((interface, {sock.id})) for interface in interfaces]
            self.logger.info("Socket#%s started." % sock.id)
        self.logger.info("All server sockets started.")
        self.logger.info("Listening at:\n" + '\n'.join([f"{url} <Socket#{sock}>" for url, sock in entrypoints]))
        
        for sock in sockets:
            sock.listen()
            self.logger.info("Socket#%s listening." % sock.id)
            
        self.logger.info("All server sockets listening.")
        self.init_time = time.time()
        while True:
            try:
                if self.auto_reload:
                    self.check_file_changes()
                active_sockets = []
                readable, _, _ = select.select([sock for sock in sockets if sock not in active_sockets], [], [], 0.1)
                for sock in readable:
                    active_sockets.append(sock)
                    client_handler = threading.Thread(target=Worker, args=(sock.get_client(), self.router, self.debug), daemon=True)
                    client_handler.start()
                    time.sleep(0.5)
            except KeyboardInterrupt:
                self.logger.critical("KeyboardInterrupt received. Press Ctrl+C again to stop the server. [5s]")
                try:
                    time.sleep(5)
                    self.logger.warning("Server not stopped. Continuing...")
                except KeyboardInterrupt:
                    self.logger.critical("KeyboardInterrupt received. Stopping server...")
                    for sock in sockets:
                        sock.close()
                    self.logger.info("Server stopped.")
                    return
            
    def check_file_changes(self):
        """
        Checks for file changes and reloads the server if any changes are detected.
        """
        for path, _, files in os.walk("."):
            for file in files:
                if file.endswith(".py") and os.path.getmtime(os.path.join(path, file)) > self.init_time:
                    self.logger.warning("File<%s> changed. Reloading server..." % file)
                    try:
                        os.execv(sys.executable, [f'"{sys.executable}"'] + [f'"{arg}"' for arg in sys.argv])
                    except:
                        self.logger.critical("An error occurred while trying to reload the server: %s" % traceback.format_exc())
                
class Worker:
    """
    Represents a worker that handles client requests.

    Args:
        socket (socket): The socket object representing the client connection.
        router (Router): The router object responsible for handling client requests.

    Attributes:
        socket (socket): The socket object representing the client connection.
        router (Router): The router object responsible for handling client requests.
        logger (Logger): The logger object for logging worker events.

    """

    def __init__(self, client, router, debug):
        self.start_time = time.time()
        self.client = client
        self.router = router
        self.debug = debug
        self.handle_request()
        
    def handle_request(self):
        """
        Handles the client request.
        """
        logger = worker_logger(id(self))
        try:
            init_time = time.time()
            data = self.client.receive()
            if len(data) == 0:
                return
            receive_time = time.time()
            request = Request(data)
            logger.info("%s %s" % (request.method, request.path))
            handler, request_mod, response_mod, params = self.router.route(request)
            if not handler:
                self.client.send(Response("404 Not Found", status=404).build())
                return
            for mod in request_mod:
                request = mod(request)
            response = handler(request, **params)
            for mod in response_mod:
                response = mod(response)
            if type(response) == Response:
                self.client.send(response.build())
            elif type(response) == tuple:
                if len(response) == 2 and type(response[0]) in [dict, list] and type(response[1]) == int:
                    self.client.send(Response(json.dumps(response[0]), status=response[1], content_type="application/json").build())
                else:
                    self.client.send(Response("500 Internal Server Error", status=500).build())
                    logger.critical("Invalid response format: %s" % response)
            else:
                self.client.send(Response(response).build())            
        except Exception as e:
            logger.critical("An error occurred while handling the request: %s" % traceback.format_exc())
            if self.debug:
                self.client.send(Response("500 Internal Server Error:\n\n%s" % traceback.format_exc(), status=500).build())
            self.client.send(Response("500 Internal Server Error", status=500).build())
        finally:
            self.client.disconnect()
        
if __name__ == "__main__":
    server = Server(5, 1024, None)
    server.start([Socket("localhost", 8080, 1024)])