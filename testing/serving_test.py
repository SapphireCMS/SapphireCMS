from sapphirecms.routing import Router
from sapphirecms.networking import Server, Socket
import multiprocessing, requests, time
import unittest
from halo import Halo


class TestServing(unittest.TestCase):
    def test_server_init(self):
        import sys, os
        sys.stdout = open(os.devnull, "w")
        sys.stderr = open(os.devnull, "w")
        server = Server(5, Router())
        server.logger.disabled = True

        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        self.assertEqual(0,0)
        
    @classmethod
    def server_run(cls, sockets):
        import sys, os
        sys.stdout = open(os.devnull, "w")
        sys.stderr = open(os.devnull, "w")
        server = Server(5, Router())
        
        server.router.add_route("/", "GET")(lambda request: "Hello, World!")
        
        server.start(sockets)
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        
    def test_server_start(self):
        p = multiprocessing.Process(target=self.server_run, args=([Socket("0.0.0.0", 4565, 1024)],))
        p.start()
        time.sleep(1)
        
        response = requests.get("http://localhost:4565")
        if response.status_code == 200:
            self.assertEqual(response.text, "Hello, World!")
        else:
            self.fail(f"Server returned status code {response.status_code}")
            
        p.terminate()
            
    def test_server_multi_socket(self):
        p = multiprocessing.Process(target=self.server_run, args=([Socket("0.0.0.0", 4566, 1024), Socket("0.0.0.0", 4567, 1024)],))
        p.start()
        time.sleep(1)
        
        r1 = requests.get("http://localhost:4566")
        r2 = requests.get("http://localhost:4567")
        self.assertEqual(r1.text, r2.text)
    
        p.terminate()
        
    def runTest(self):
        print("Running Serving tests...")
        fails = 0
        with Halo(text="Running Serving.server_init", spinner="dots2") as spinner:
            try:
                self.test_server_init()
                spinner.succeed()
            except Exception as e:
                spinner.fail()
                fails += 1
        with Halo(text="Running Serving.server_start", spinner="dots2") as spinner:
            try:
                self.test_server_start()
                spinner.succeed()
            except Exception as e:
                spinner.fail()
                fails += 1
        with Halo(text="Running Serving.server_multi_socket", spinner="dots2") as spinner:
            try:
                self.test_server_multi_socket()
                spinner.succeed()
            except Exception as e:
                spinner.fail()
                fails += 1

        if fails == 0:
            print("All Serving tests passed.")
        else:
            print(f"{fails} Serving tests failed.")
        
if __name__ == "__main__":
    unittest.main()