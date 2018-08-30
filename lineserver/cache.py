from collections import OrderedDict
from typing import Dict
from . import LineNum
from .directory import Directory


class _CacheRecord(object):
    def __init__(self, the_bytes: bytes):
        self.bytes = the_bytes
        self.age = 0

    def visit_and_age(self) -> int:
        self.age += 1
        return self.age


class Cache(object):
    age_threshold = 4

    def __init__(self, file_name, storage_bytes):
        self.file_name = file_name

        self.storage_bytes = storage_bytes
        self.stored_bytes = 0
        self.clock_ptr = 0

        self.directory = Directory(file_name, 2 ** 10)

        self.records = OrderedDict()  # type: Dict[LineNum, _CacheRecord]

    def get_bytes_for_line(self, line_num: LineNum) -> bytes:
        if line_num not in self.records:
            self.read_in_line(line_num)
        return self.records[line_num].bytes

    def read_in_line(self, line_num: LineNum):
        closest_line, offset = self.directory.find_offset(line_num)
        with open(self.file_name, 'rb') as file_handle:
            file_handle.seek(offset)
            current_line = closest_line
            while current_line != line_num:
                file_handle.readline()
                current_line += 1

            line = file_handle.readline()

        while len(line) + self.stored_bytes > self.storage_bytes:
            self.evict()

        self.stored_bytes += len(line)
        self.records[line_num] = _CacheRecord(line)

    def evict(self) -> None:
        while True:
            for i, record in self.records:
                if record.visit_and_age() > self.age_threshold:
                    del(self.records[i])
                    self.stored_bytes -= len(record.bytes)
                    return
