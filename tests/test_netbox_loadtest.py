import unittest

from bin.netbox_loadtest import colnum_string


class TestColNumString(unittest.TestCase):

    def test_colnum_string_valid(self):
        self.assertEqual('AA', colnum_string(27))
