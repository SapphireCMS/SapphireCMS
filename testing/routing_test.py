from sapphirecms.routing import Router, Route, ProxyRouter
from sapphirecms.networking import Request
import unittest
from halo import Halo


class TestRouting(unittest.TestCase):
    def test_router_init(self):
        router = Router()
        router.logger.disabled = True
        
        self.assertEqual(router.routes, [])
        
    def test_router_add_route(self):
        router = Router()
        router.logger.disabled = True
        
        router.add_route("/", "GET")(lambda request: "Hello, World!")
        self.assertIn("GET /", [str(route) for route in router.routes])
        
    def test_router_route(self):
        router = Router()
        router.logger.disabled = True
        
        @router.add_route("/", "GET")
        def index(request):
            return "Hello, World!"
        
        self.assertEqual(router.route(Request("GET / HTTP/1.1\r\n\r\n"))[0], index)
        
    def test_parametric_route(self):
        router = Router()
        router.logger.disabled = True
        
        router.add_route("/<name>", "GET")(lambda request, name: f"Hello, {name}!")
        
        n = "World"
        request = Request(f"GET /{n} HTTP/1.1\r\n\r\n")
        
        handler, _, _, params = router.route(request)
        
        self.assertEqual(handler(request, **params), f"Hello, {n}!")
        
    def test_request_mod(self):
        router = Router()
        router.logger.disabled = True
        
        def request_mod(request):
            request.data["test"] = "Hello, World!"
            return request
            
        @router.add_route("/", "GET", [request_mod])
        def index(request):
            return request.data["test"]
        
        request = Request("GET / HTTP/1.1\r\n\r\n")
        handler, request_mods, _, params = router.route(request)
        
        for mod in request_mods:
            request = mod(request)
        response = handler(request, **params)
        
        self.assertEqual(response, "Hello, World!")
        
    def test_response_mod(self):
        router = Router()
        router.logger.disabled = True
        
        def response_mod(request, response):
            response = response + "!"
            return response
            
        @router.add_route("/", "GET", [], [response_mod])
        def index(request):
            return "Hello, World!"
        
        request = Request("GET / HTTP/1.1\r\n\r\n")
        handler, _, response_mods, params = router.route(request)
        
        response = handler(request, **params)
        for mod in response_mods:
            response = mod(request, response)
        
        self.assertEqual(response, "Hello, World!!")
        
    def test_subrouter_init(self):
        router = Router()
        router.logger.disabled = True
        
        subrouter = Router(prefix="/sub")
        subrouter.logger.disabled = True
        
        router.add_subrouter(subrouter)
        
        self.assertIn(subrouter, router.subrouters.values())
        
    def test_subrouter_route(self):
        router = Router()
        router.logger.disabled = True
        
        subrouter = Router(prefix="/sub")
        subrouter.logger.disabled = True
        
        router.add_route("/", "GET")(lambda request: "Hello, World!")
        subrouter.add_route("/", "GET")(lambda request: "Hello, Again!")
        
        router.add_subrouter(subrouter)
        
        request = Request("GET / HTTP/1.1\r\n\r\n")
        handler, _, _, params = router.route(request)
        
        self.assertEqual(handler(request, **params), "Hello, World!")
        
        request = Request("GET /sub/ HTTP/1.1\r\n\r\n")
        handler, _, _, params = router.route(request)
        
        self.assertEqual(handler(request, **params), "Hello, Again!")

    def test_subrouter_parametric_route(self):
        router = Router()
        router.logger.disabled = True
        
        subrouter = Router(prefix="/sub")
        subrouter.logger.disabled = True
        
        router.add_route("/", "GET")(lambda request: "Hello, World!")
        subrouter.add_route("/<name>", "GET")(lambda request, name: f"Hello, {name}!")
        
        router.add_subrouter(subrouter)
        
        n = "Again"
        request = Request(f"GET /sub/{n} HTTP/1.1\r\n\r\n")
        
        handler, _, _, params = router.route(request)
        
        self.assertEqual(handler(request, **params), f"Hello, {n}!")
        
    def test_proxy_init(self):
        router = Router()
        router.logger.disabled = True
        
        proxy = ProxyRouter(name="PR1", internal_path="/proxy", external_url="https://jsonplaceholder.typicode.com/todos/")
        proxy.logger.disabled = True
        
        router.add_proxy(proxy)
        
        self.assertIn(proxy, router.subrouters.values())
        
    def test_proxy_route(self):
        import json
        
        router = Router()
        router.logger.disabled = True
        
        proxy = ProxyRouter(name="PR1", internal_path="/proxy", external_url="https://jsonplaceholder.typicode.com/todos/")
        proxy.logger.disabled = True
        
        router.add_proxy(proxy)
        
        request = Request("GET /proxy/1 HTTP/1.1\r\n\r\n")
        handler, _, _, params = router.route(request)
        
        response = handler(request, **params)
        
        json_response = json.loads(response.body)
        
        self.assertIn("userId", json_response)
        self.assertIn("id", json_response)
        self.assertIn("title", json_response)
        self.assertIn("completed", json_response)
        
    def runTest(self):
        print("Running Routing tests...")
        fails = 0
        with Halo(text="Running Routing.router_init", spinner="dots2") as spinner:
            try:
                self.test_router_init()
                spinner.succeed()
            except Exception as e:
                spinner.fail()
                fails += 1
        with Halo(text="Running Routing.router_add_route", spinner="dots2") as spinner:
            try:
                self.test_router_add_route()
                spinner.succeed()
            except Exception as e:
                spinner.fail()
                fails += 1
        with Halo(text="Running Routing.router_route", spinner="dots2") as spinner:
            try:
                self.test_router_route()
                spinner.succeed()
            except Exception as e:
                spinner.fail()
                fails += 1
        with Halo(text="Running Routing.parametric_route", spinner="dots2") as spinner:
            try:
                self.test_parametric_route()
                spinner.succeed()
            except Exception as e:
                spinner.fail()
                fails += 1
        with Halo(text="Running Routing.request_mod", spinner="dots2") as spinner:
            try:
                self.test_request_mod()
                spinner.succeed()
            except Exception as e:
                spinner.fail()
                fails += 1
        with Halo(text="Running Routing.response_mod", spinner="dots2") as spinner:
            try:
                self.test_response_mod()
                spinner.succeed()
            except Exception as e:
                spinner.fail()
                fails += 1
        with Halo(text="Running Routing.subrouter_init", spinner="dots2") as spinner:
            try:
                self.test_subrouter_init()
                spinner.succeed()
            except Exception as e:
                spinner.fail()
                fails += 1
        with Halo(text="Running Routing.subrouter_route", spinner="dots2") as spinner:
            try:
                self.test_subrouter_route()
                spinner.succeed()
            except Exception as e:
                spinner.fail()
                fails += 1
        with Halo(text="Running Routing.subrouter_parametric_route", spinner="dots2") as spinner:
            try:
                self.test_subrouter_parametric_route()
                spinner.succeed()
            except Exception as e:
                spinner.fail()
                fails += 1

        if fails == 0:
            print("All Routing tests passed.")
        else:
            print(f"{fails} Routing tests failed.")
        
if __name__ == "__main__":
    unittest.main()