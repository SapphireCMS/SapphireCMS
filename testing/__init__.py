from html_test import TestHTML
from routing_test import TestRouting
import unittest

class TestSuite(unittest.TestSuite):
    def __init__(self):
        super().__init__([TestHTML(), TestRouting()])
        
if __name__ == "__main__":
    unittest.TextTestRunner().run(TestSuite())