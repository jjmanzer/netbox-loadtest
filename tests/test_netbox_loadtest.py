import unittest

from bin.netbox_loadtest import colnum_string


class TestNetBoxKLoadTest(unittest.TestCase):

    def test_colnum_string_valid_singleletter(self):
        self.assertEqual('A', colnum_string(1))

    def test_colnum_string_valid_two_letter(self):
        self.assertEqual('AA', colnum_string(27))

    def test_colnum_string_valid_three_letter(self):
        self.assertEqual('AAA', colnum_string(703))
