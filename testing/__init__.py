from html_test import TestHTML
from routing_test import TestRouting
from serving_test import TestServing
import unittest

class TestSuite(unittest.TestSuite):
    def __init__(self):
        super().__init__([TestHTML(), TestRouting(), TestServing()])
        
if __name__ == "__main__":
    unittest.TextTestRunner().run(TestSuite())