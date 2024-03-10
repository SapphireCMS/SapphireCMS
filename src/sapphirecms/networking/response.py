class Response:
    """
    A class for handling responses.
    """
    def __init__(self, body, status="200 OK", content_type="text/html", cookies={}, headers={}):
        self.body = body
        self.version = "HTTP/1.1"
        self.status = status
        self.content_type = content_type
        self._cookies = cookies
        self.headers = {
            "Content-Type": self.content_type,
            "Connection": "close",
            "Set-Cookie": "; ".join(["%s=%s" % (cookiename, cookievalue) for cookiename, cookievalue in self._cookies.items()])
        }
        self.headers.update(headers)
        
    def __str__(self):
        self.headers["Content-Length"] = len(self.body)
        return "%s %s\n%s\n\n%s" % (self.version, self.status, "\n".join(["%s: %s" % (header, self.headers[header]) for header in self.headers]), self.body)
    
    def recalculate(self):
        """
        Recalculates the headers.
        """
        self.headers["Set-Cookie"] = "; ".join(["%s=%s" % (cookiename, cookievalue) for cookiename, cookievalue in self._cookies.items()])
        self.headers["Content-Length"] = len(self.body)
    
    def build(self):
        """
        Builds the response.
        """
        self.recalculate()
        status_line = ("%s %s" % (self.version, self.status)).encode("utf-8")
        headers = b"\n".join([b"%s: %s" % (str(header).encode("utf-8") if type(header) in [str, int] else header, str(value).encode("utf-8") if type(value) in [str, int] else value) for header, value in self.headers.items()])
        body = str(self.body).encode("utf-8") if type(self.body) in [str, int] else self.body
        return b"%s\r\n%s\r\n\r\n%s" % (status_line, headers, body)

if __name__ == "__main__":
    response = Response(b"Hello, world!")
    print(response.build())