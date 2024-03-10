import logging, sys, os
from sapphirecms.networking.response import Response
from sapphirecms.networking.request import Request
from sapphirecms.logs import LogFormatter
from typing import Callable
import mimetypes

import requests
from urllib.parse import urlparse

class Router:
    """
    Represents a router that handles client requests.

    Args:
        routes (list): A list of routes.
        logger (Logger): The logger object for logging router events.

    Attributes:
        routes (list): A list of routes.
        logger (Logger): The logger object for logging router events.

    """

    def __init__(self, name: str = "MAIN", prefix: str = "", static_dir: str = "static", static_prefix: str = "/static", ctx: str = ""):
        self.routes = []
        self.subrouters = {}
        self.name = name
        self.prefix = prefix
        self.static_dir = static_dir
        self.static_prefix = prefix + static_prefix
        
        if ctx != "":
            self.static_dir = os.path.join(os.path.dirname(sys.modules[ctx].__file__), self.static_dir)
        
        self.logger = logging.getLogger(f"Router<{self.name}>")
        self.logger.setLevel(logging.DEBUG)
        stdout_handler = logging.StreamHandler(sys.stdout)
        stdout_handler.setFormatter(LogFormatter(("%s ROUTER" % self.name.upper())))
        self.logger.addHandler(stdout_handler)
        self.logger.addHandler(logging.FileHandler("logs/server.log"))
        
    def add_route(self, path: str, methods: list = ["GET"], request_mod: list = [], response_mod: list = []):
        """
        Adds a route to the router.

        Args:
            route (Route): The route to be added.

        """
        def decorator(handler):
            self.routes.append(Route(f'{self.prefix}{path}', methods, request_mod, response_mod, handler))
            return handler
        return decorator
        
    def add_subrouter(self, subrouter, rule: Callable = None):
        """
        Adds a subrouter to the router.

        Args:
            path (str): The path of the subrouter.
            subrouter (Router): The subrouter to be added.

        """
        if not isinstance(subrouter, Router):
            raise Exception("Subrouter must be of type Router")
        subrouter.prefix = f'{self.prefix}{subrouter.prefix}'
        if not rule:
            if subrouter.prefix:
                rule = lambda request: request.path.startswith(subrouter.prefix)
            else:
                rule = lambda request: True
        if not callable(rule):
            raise Exception("Rule must be a callable function")
        
        self.subrouters[rule] = subrouter
        self.logger.info("Added subrouter<%s> to router<%s>" % (subrouter.name, self.name))
        
    def add_proxy(self, proxy):
        """
        Adds a proxy to the router.

        Args:
            proxy (ProxyRouter): The proxy to be added.

        """
        if not isinstance(proxy, ProxyRouter):
            raise Exception("Proxy must be of type ProxyRouter")
        rule = lambda request: request.path.startswith(f'{self.prefix}{proxy.internal_path}')
        self.subrouters[rule] = proxy
        self.logger.info("Added proxy<%s> to router<%s>" % (f'{self.prefix}{proxy.internal_path}', self.name))
    
    def route(self, request: Request, parent_prefix: str = ""):
        """
        Routes a request to the appropriate handler.

        Args:
            request (Request): The request object to be routed.

        """
        for route in self.routes:
            if route.matches(request, parent_prefix):
                self.logger.info("Found matching route")
                return route.handler, route.request_mod, route.response_mod, route.extract_params(request)
        for rule, subrouter in self.subrouters.items():
            if rule(request):
                self.logger.info("Routing request to subrouter<%s>" % subrouter.name)
                return subrouter.route(request, f'{parent_prefix}{subrouter.prefix}')
        if request.path.startswith(self.static_prefix):
            self.logger.info("Routing request to static handler")
            path = request.path[len(self.static_prefix):]
            if path.startswith("/"):
                path = path[1:]
            return self.static_handler, [], [], {"path": path}
        return None, [], [], {}
    
    def static_handler(self, request: Request, path: str):
        """
        Handles static file requests.

        Args:
            path (str): The path of the static file.

        Returns:
            Response: The response object containing the static file.

        """
        try:
            print(f"{self.static_dir}/{path}"[:-1])
            local_path = f"{self.static_dir}/{path}"[:-1].replace("/", os.sep)
            with open(local_path, "rb") as f:
                if "." in local_path:
                    content_type = mimetypes.MimeTypes().guess_type(local_path)
                    return Response(f.read(), content_type=content_type[0])
                return Response(f.read())
        except:
            return Response("404 Not Found", status=404)
        
class ProxyRouter(Router):
    """
    Represents a router that proxies requests to an external server.
    
    Args:
        name (str): The name of the proxy router.
        internal_path (str): The path of the proxy router.
        external_url (str): The URL of the external server.
        headers (dict): The headers to be sent with the request.
        
    Attributes:
        internal_path (str): The path of the proxy router.
        external_url (str): The URL of the external server.
        headers (dict): The headers to be sent with the request.
        
    """
    
    def __init__(self, name: str, internal_path: str, external_url: str, request_headers: dict = {}, response_headers: dict = {}, url_rewrite: Callable = lambda x: x):
        self.name = name
        self.internal_path = self.prefix = internal_path
        self.external_url = external_url
        self.request_headers = request_headers
        self.response_headers = response_headers
        self.url_rewrite = url_rewrite
        
        self.logger = logging.getLogger(f"ProxyRouter<{self.internal_path}>")
        
    def route(self, request: Request, parent_prefix: str = ""):
        """
        Routes a request to the appropriate handler.

        Args:
            request (Request): The request object to be routed.

        """
        self.logger.info("Routing request to external server")
        return self.get_proxy_handler(request, parent_prefix), [], [], {}
    
    def get_proxy_handler(self, request: Request, parent_prefix: str):
        """
        Returns a handler function that proxies the request to the external server.

        Args:
            request (Request): The request object to be routed.

        Returns:
            function: The handler function that proxies the request to the external server.

        """
        def handler(request: Request):
            """
            Proxies the request to the external server.

            Args:
                path (str): The path of the request.

            Returns:
                Response: The response object containing the response from the external server.

            """
            url = self.url_rewrite(request.path[len(parent_prefix):])
            headers = request.headers
            headers.update(self.request_headers.get(url, self.request_headers.get("*", {})))
            response = requests.request(request.method, f"{self.external_url}{url}", headers=headers, data=request.body)
            response_headers = response.headers
            response_headers.pop("Content-Encoding", None)
            response_headers.pop("Transfer-Encoding", None)
            response_headers.update(self.response_headers.get(url, self.response_headers.get("*", {})))
            
            response_body = self.adapt_response_body(response.content, path=urlparse(f"{self.external_url}{url}"))
            return Response(response_body, status=response.status_code, headers=response_headers)
        return handler
    
    def adapt_response_body(self, body, path):
        """
        Adapts the response body.

        Args:
            body (bytes): The body of the response.
            headers (dict): The headers of the response.

        Returns:
            bytes: The adapted body of the response.

        """
        
        return body
        
        if type(body) == str:
            body = body.encode()
        body = body.replace(f"<head>".encode(), f"<head><base href='{path.scheme}://{path.netloc}/'>".encode())
            
        return body
    
class Route:
    """
    Represents a route.

    Args:
        path (str): The path of the route.
        method (str): The method of the route.
        handler (function): The handler function of the route.

    Attributes:
        path (str): The path of the route.
        method (str): The method of the route.
        handler (function): The handler function of the route.

    """

    def __init__(self, path: str, methods: list, request_mod: list, response_mod: list, handler: Callable):
        self.path = path
        self.methods = methods
        self.handler = handler
        self.request_mod = request_mod
        self.response_mod = response_mod

    def matches(self, request: Request, prefix: str = ""):
        """
        Checks whether the route matches the request.

        Args:
            request (Request): The request object to be matched.

        Returns:
            bool: True if the route matches the request, False otherwise.

        """
        if request.method not in self.methods:
            return False
        
        if self.path == request.path:
            return True
        
        path_components = list(filter(lambda x: x != "", self.path.split("/")))
        if request.path.startswith(prefix):
            request_components = list(filter(lambda x: x != "", request.path.split("/")))
            
        if request.path == self.path:
            return True
        if len(path_components) != len(request_components):
            return False
        if len(path_components) == 0:
            return False
        # print(path_components, request_components, self.path, request.path)
        for i in range(len(path_components)):
            # print(path_components[i], request_components[i])
            if path_components[i].startswith("<") and path_components[i].endswith(">"):
                if ":" not in path_components[i][1:-1]:
                    data_type = "string"
                else:
                    data_type = path_components[i][1:-1].split(":")[0]
                value = request_components[i]
                if data_type == "int":
                    try:
                        int(value)
                    except:
                        return False
                elif data_type == "string":
                    pass
                else:
                    try:
                        globals()[data_type](value)
                    except:
                        return False
            else:
                if path_components[i] != request_components[i]:
                    return False
            
        return True
    
    def extract_params(self, request: Request):
        """
        Extracts the parameters from the request.

        Args:
            request (Request): The request object to be matched.

        Returns:
            dict: The dictionary of parameters.

        """
        if not self.matches(request):
            return {}
        path_components = self.path.split("/")
        request_components = request.path.split("/")
        
        params = {}
        for i in range(len(path_components)):
            if path_components[i].startswith("<") and path_components[i].endswith(">"):
                if ":" not in path_components[i][1:-1]:
                    data_type = "string"
                    var_name = path_components[i][1:-1]
                else:
                    data_type = path_components[i][1:-1].split(":")[0]
                    var_name = path_components[i][1:-1].split(":")[1]
                value = request_components[i]
                if data_type == "int":
                    params[var_name] = int(value)
                elif data_type == "string":
                    params[var_name] = value
                else:
                    try:
                        params[var_name] = globals()[data_type](value)
                    except:
                        params[var_name] = value
                        # print("Warning: Could not convert parameter to specified type. Using string instead.")
                        self.logger.warning("Could not convert parameter to specified type. Using string instead.")
        return params
    
    def __str__(self):
        """
        Returns the string representation of the route.

        Returns:
            str: The string representation of the route.

        """
        return "%s %s" % (self.methods, self.path)
    
    def __repr__(self):
        """
        Returns the string representation of the route.

        Returns:
            str: The string representation of the route.

        """
        return str(self)