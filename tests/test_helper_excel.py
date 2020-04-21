import unittest

from openpyxl import Workbook

from helpers.excel import add_worker_data_to_sheet, colnum_string


class TestHelperExcel(unittest.TestCase):
    def test_colnum_string_valid_singleletter(self):
        self.assertEqual("A", colnum_string(1))

    def test_colnum_string_valid_two_letter(self):
        self.assertEqual("AA", colnum_string(27))

    def test_colnum_string_valid_three_letter(self):
        self.assertEqual("AAA", colnum_string(703))

    def test_add_worker_data_to_sheet_1_worker(self):
        workbook = Workbook()
        sheet = workbook.create_sheet("1 workers")
        worker_data = {
            "10.0.0.0/30": {
                "test_get_next_free_address": {
                    "prefix": "10.0.0.0/30",
                    "allocate": {"data": {"10.0.0.1": 0.01, "10.0.0.2": 0.02}},
                    "deallocate": {"data": {"10.0.0.1": 0.01, "10.0.0.2": 0.02}},
                },
                "test_get_next_free_address_fragmented": {
                    "prefix": "10.0.0.0/30",
                    "allocate": {"data": {"10.0.0.1": 0.01, "10.0.0.2": 0.02}},
                    "deallocate": {"data": {"10.0.0.1": 0.01, "10.0.0.2": 0.02}},
                },
                "test_scattered_assignments": {
                    "prefix": "10.0.0.0/30",
                    "allocate": {"data": {"10.0.0.2": 0.02}},
                    "deallocate": {"data": {"10.0.0.2": 0.02}},
                },
            }
        }

        add_worker_data_to_sheet(worker_data, sheet)

        self.assertEqual(sheet["C1"].value, "worker 1")
        self.assertEqual(sheet["C2"].value, "test_get_next_free_address")
        self.assertEqual(sheet["C3"].value, "allocate")
        self.assertEqual(sheet["C4"].value, 0.01)
