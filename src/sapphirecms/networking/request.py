class Request:
    """
    A class for handling requests.
    """
    def __init__(self, request_data):
        self.method = None
        self.path = None
        self.version = None
        self.headers = {}
        self.body = None
        self.parse(request_data)
        
    def parse(self, request_data):
        """
        Parses the request data.
        """
        if type(request_data) == bytes:
            request_data = request_data.decode("utf-8")
        lines = request_data.split("\r\n")
        request_line = lines[0].split(" ")
        self.method = request_line[0]
        self.path = request_line[1].split("?")[0]
        if not self.path.endswith("/"):
            self.path += "/"
        if not self.path.startswith("/"):
            self.path = "/" + self.path
        self.version = request_line[2]
        for line in lines[1:]:
            if not line:
                break
            header = line.split(": ")
            self.headers[header[0]] = header[1]
            
        self.data = {
            "GET": self.path.split("?")[1] if "?" in self.path else "",
            "POST": "\r\n".join(lines[lines.index("") + 1:]),
            "COOKIE": [{cookie.split("=")[0]: cookie.split("=")[1]} for cookie in self.headers["Cookie"].split("; ")] if "Cookie" in self.headers else {},
        }

if __name__ == "__main__":
    request = Request(b"GET / HTTP/1.1\r\nHost: localhost:8080\r\nUser-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:86.0) Gecko/20100101 Firefox/86.0\r\nAccept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8\r\nAccept-Language: en-US,en;q=0.5\r\nAccept-Encoding: gzip, deflate\r\nConnection: keep-alive\r\nUpgrade-Insecure-Requests: 1\r\n\r\n")
    print(request.method)
    print(request.path)
    print(request.version)
    print(request.headers)
    print(request.body)