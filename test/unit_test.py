import unittest
import math
import lineserver.directory
import lineserver.cache


class DirectoryTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.long_file_name = "../frankenstein.txt"
        i = -1
        with open(cls.long_file_name, 'rb') as f:
            for i, _ in enumerate(f):
                pass
        cls.num_lines = i + 1

    def test_only_one_record_allowed(self):
        directory = lineserver.directory.Directory(self.long_file_name, 1)
        self.assertEqual(len(directory._records), 1, "Only one record is allowed")
        self.assertEqual(directory._records[0].line_num, 1, "First record should always be for first line")
        self.assertEqual(directory._records[0].offset, 0, "First record should always have offset zero")

    def test_no_allowed_records_exception(self):
        with self.assertRaises(ZeroDivisionError):
            lineserver.directory.Directory(self.long_file_name, 0)

    def test_bad_file_name(self):
        with self.assertRaises(FileNotFoundError):
            lineserver.directory.Directory(self.long_file_name + "Bogus", 1)

    def test_more_records_allowed_than_needed(self):
        directory = lineserver.directory.Directory(self.long_file_name, self.num_lines + 1000)
        self.assertEqual(directory._records[0].line_num, 1, "First record should always be for first line")
        self.assertEqual(directory._records[0].offset, 0, "First record should always have offset zero")

        self.assertEqual(len(directory._records), self.num_lines, "Should have a record for every line")

    def test_limited_number_of_records(self):
        allowed_records = self.num_lines - 1000
        directory = lineserver.directory.Directory(self.long_file_name, allowed_records)
        self.assertEqual(directory._records[0].line_num, 1, "First record should always be for first line")
        self.assertEqual(directory._records[0].offset, 0, "First record should always have offset zero")

        self.assertLessEqual(len(directory._records), allowed_records, "Should honor number of records designated")
        self.assertEqual(directory._records[1].line_num - directory._records[0].line_num,
                         math.ceil(self.num_lines / allowed_records),
                         "Should have correct granularity")

