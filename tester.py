import unittest
import hashcash
from hashlib import sha256
from hashcash import test_bytes


class TestFonctions(unittest.TestCase):
    def test_test_bytes(self):
        self.assertEqual(test_bytes(sha256("426479724".encode("utf-8")).digest(), 32), True)
        self.assertEqual(test_bytes(sha256("665782".encode("utf-8")).digest(), 22), True)
        

if __name__ == '__main__':
    unittest.main()