import logging, time, sys
import os

class LogFormatter(logging.Formatter):
    """
    Represents a custom log formatter.
    """
    COLOR_CODES = {
        logging.DEBUG: "\033[94m\033[1m",
        logging.INFO: "\033[92m",
        logging.WARNING: "\033[93m\033[1m",
        logging.ERROR: "\033[91m\033[1m",
        logging.CRITICAL: "\033[91m\033[1m\033[4m\033[5m"
    }
    
    def __init__(self, name=None):
        super().__init__("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        self.name = name
    
    def format(self, record):
        return ("%s[%s] %s:\033[0m %s:: %s" % (self.COLOR_CODES[record.levelno], self.name, record.levelname, time.strftime("%d-%m-%Y@%H:%M:%S", time.localtime(record.created)), record.getMessage()))
    
class MonoLogFormatter(LogFormatter):
    """
    Represents a monochrome log formatter.
    """
    def format(self, record):
        return ("[%s] %s: %s:: %s" % (self.name, record.levelname, time.strftime("%d-%m-%Y@%H:%M:%S", time.localtime(record.created)), record.getMessage()))


loggers = {
    "Server": logging.getLogger("Server"),
    "Socket": logging.getLogger("Socket"),
    "Client": logging.getLogger("Client"),
    "Worker": logging.getLogger("Worker")
}


def changestreamhandler(name, streamhandler=None, formatter=None, level=logging.DEBUG):
    l = logging.getLogger(name)
    if not formatter:
        formatter = LogFormatter(name)
    if l.hasHandlers():
        l.handlers.clear()
    if streamhandler:
        streamhandler.setFormatter(formatter)
        l.addHandler(streamhandler)
    file_handler = logging.FileHandler("logs/server.log")
    file_handler.setFormatter(MonoLogFormatter(name))
    l.addHandler(file_handler)
    l.setLevel(level)
    return l


server_logger = lambda: changestreamhandler("Server", logging.StreamHandler(sys.stdout), LogFormatter("SERVER"))
socket_logger = lambda id: changestreamhandler("Socket", logging.StreamHandler(sys.stdout), LogFormatter("SOCKET#%s" % id))
client_logger = lambda address: changestreamhandler("Client", logging.StreamHandler(sys.stdout), LogFormatter("CLIENT::%s:%s" % (address[0], address[1])))
worker_logger = lambda id: changestreamhandler("Worker", logging.StreamHandler(sys.stdout), LogFormatter("WORKER#%s" % id))

os.makedirs("logs", exist_ok=True)