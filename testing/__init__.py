from html_test import TestHTML
import unittest

class TestSuite(unittest.TestSuite):
    def __init__(self):
        super().__init__([TestHTML()])
        
if __name__ == "__main__":
    unittest.TextTestRunner().run(TestSuite())