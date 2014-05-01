import unittest
from hashlib import sha256
from hashcash import test_bytes, test_byte


class TestFonctions(unittest.TestCase):

    def test_test_byte(self):
        self.assertEqual(test_byte(0b00000000, 8), True)
        self.assertEqual(test_byte(0b00000001, 7), True)
        self.assertEqual(test_byte(0b00000011, 6), True)
        self.assertEqual(test_byte(0b00000111, 5), True)
        self.assertEqual(test_byte(0b00001111, 4), True)
        self.assertEqual(test_byte(0b00011111, 3), True)
        self.assertEqual(test_byte(0b00111111, 2), True)
        self.assertEqual(test_byte(0b01111111, 1), True)
        self.assertEqual(test_byte(0b11111111, 0), True)

    def test_test_bytes(self):
        self.assertEqual(test_bytes(sha256("426479724".encode("utf-8")).digest(), 32), True)
        self.assertEqual(test_bytes(sha256("665782".encode("utf-8")).digest(), 22), True)
        self.assertEqual(test_bytes(sha256("886".encode("utf-8")).digest(), 12), True)
        self.assertEqual(test_bytes(sha256("8".encode("utf-8")).digest(), 2), True)



if __name__ == '__main__':
    unittest.main()