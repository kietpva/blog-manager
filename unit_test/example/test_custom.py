import unittest


class CustomTestCase(unittest.TestCase):
    def assertAllIntegers(self, values):
        for value in values:
            self.assertIsInstance(
                value,
                int,
            )
