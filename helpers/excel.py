"""
A helper for populating the excel sheets with test results.
"""


def add_worker_data_to_sheet(worker_data: dict, sheet: object):
    """Add all the worker reports in worker_data to the workbook.

    We create a tab for every level of concurrency from 1 - N.
    Each tab contains 6 datsets (3 tests with 2 phases each) worth of raw data, avg, stdv and total.
    Hopefully the raw data will make sure useful data visualization which is not included in this code.
    """

    for worker_id, worker_report in enumerate(worker_data.values()):
        footer_row = (
            len(worker_report["test_get_next_free_address"]["allocate"]["data"]) + 6
        )
        sheet[f"B{ footer_row }"] = "mean"
        sheet[f"B{ footer_row + 1 }"] = "stdev"
        sheet[f"B{ footer_row + 2 }"] = "total"

        for test_name, test_id in {
            "test_get_next_free_address": 1,
            "test_get_next_free_address_fragmented": 2,
            "test_scattered_assignments": 3,
        }.items():
            row = 1
            column = (worker_id * 6) + (test_id * 2) + 1
            lcolumn = colnum_string(column)  # get the letter value for y-coord
            lcolumn2 = colnum_string(column + 1)  # get the letter value for y-coord

            sheet.cell(row=1, column=column).value = f"worker { worker_id + 1 }"
            sheet.cell(row=1, column=column + 1).value = f"worker { worker_id + 1}"
            sheet.cell(row=2, column=column).value = test_name
            sheet.cell(row=2, column=column + 1).value = test_name
            sheet.cell(row=3, column=column).value = "allocate"
            sheet.cell(row=3, column=column + 1).value = "deallocate"

            for id, value in enumerate(
                worker_report[test_name]["allocate"]["data"].values()
            ):
                sheet.cell(row=id + 4, column=column).value = value
                if (id + 4) > row:
                    row = id + 4

            sheet.cell(
                row=footer_row, column=column
            ).value = f"=AVERAGE({ lcolumn }4:{ lcolumn }{ row })"
            sheet.cell(
                row=footer_row + 1, column=column
            ).value = f"=STDEV({ lcolumn }4:{ lcolumn }{ row })"
            sheet.cell(
                row=footer_row + 2, column=column
            ).value = f"=SUM({ lcolumn }4:{ lcolumn }{ row })"

            for id, key in enumerate(
                worker_report[test_name]["deallocate"]["data"].keys()
            ):
                sheet.cell(row=id + 4, column=column + 1).value = worker_report[
                    test_name
                ]["deallocate"]["data"][key]
                if (id + 4) > row:
                    row = id + 4

            sheet.cell(
                row=footer_row, column=column + 1
            ).value = f"=AVERAGE({ lcolumn2 }4:{ lcolumn2 }{ row })"
            sheet.cell(
                row=footer_row + 1, column=column + 1
            ).value = f"=STDEV({ lcolumn2 }4:{ lcolumn2 }{ row })"
            sheet.cell(
                row=footer_row + 2, column=column + 1
            ).value = f"=SUM({ lcolumn2 }4:{ lcolumn2 }{ row })"


def colnum_string(n):
    """credit to https://stackoverflow.com/questions/23861680/convert-spreadsheet-number-to-column-letter#"""
    string = ""
    while n > 0:
        n, remainder = divmod(n - 1, 26)
        string = chr(65 + remainder) + string
    return string
