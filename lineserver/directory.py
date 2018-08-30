import bisect
import math
from typing import List
from . import LineNum, Offset


class _DirectoryRecord(object):
    def __init__(self, line_num: LineNum, offset: Offset):
        self.line_num = line_num
        self.offset = offset

    def __lt__(self, other):
        return self.line_num < other.line_num


class Directory(object):
    def __init__(self, file_name, max_num_records):
        self.records = []  # type: List[_DirectoryRecord]

        with open(file_name, 'rb') as file_handle:
            i = -1
            for i, _ in enumerate(file_handle):
                pass
            num_lines = i + 1

            record_granularity = math.ceil(num_lines / max_num_records)

            file_handle.seek(0)
            for i, line in enumerate(file_handle):
                if i % record_granularity == 2:
                    line_num = i + 1
                    self.records.append(_DirectoryRecord(line_num, file_handle.tell()))

    def find_offset(self, line_num: LineNum) -> (LineNum, Offset):
        index = bisect.bisect_left(self.records, _DirectoryRecord(line_num, 0))
        record = self.records[index]
        return record.line_num, record.offset
