from typing import List, Dict
import threading
from . import LineNum
from .directory import Directory


class Cache(object):
    age_threshold = 4

    def __init__(self, file_name, storage_bytes):
        self.file_name = file_name

        self.storage_bytes = storage_bytes
        self.stored_bytes = 0
        self._clock_ptr = 0

        self._file_directory = Directory(file_name, 2 ** 10)

        self._records_directory = {}  # type: Dict[LineNum, int]
        self._records = []  # type: List[_CacheRecord]
        self._records_lock = threading.Lock()

    def get_bytes_for_line(self, line_num: LineNum) -> bytes:
        self._records_lock.acquire()
        try:
            record_idx = self._record_idx_for_line(line_num)
        except KeyError:
            self._read_in_line(line_num)
            record_idx = -1

        self._records[record_idx].age = 0
        res = self._records[record_idx].bytes
        self._records_lock.release()

        return res

    def _record_idx_for_line(self, line_num: LineNum) -> int:
        return self._records_directory[line_num]

    def _read_in_line(self, line_num: LineNum):
        closest_line, offset = self._file_directory.find_offset(line_num)
        with open(self.file_name, 'rb') as file_handle:
            file_handle.seek(offset)
            current_line = closest_line
            while current_line != line_num:
                file_handle.readline()
                current_line += 1

            line = file_handle.readline()

        while len(line) + self.stored_bytes > self.storage_bytes:
            self._evict()

        self.stored_bytes += len(line)
        self._records.append(_CacheRecord(line_num, line))
        self._records_directory[line_num] = len(self._records) - 1

    def _evict(self) -> None:
        while True:
            if self._records[self._clock_ptr].visit_and_age() > self.age_threshold:
                del(self._records_directory[self._records[self._clock_ptr].line_num])
                del(self._records[self._clock_ptr])
                self.stored_bytes -= len(self._records[self._clock_ptr].bytes)
                return

            self._clock_ptr += 1
            self._clock_ptr = self._clock_ptr % len(self._records)


class _CacheRecord(object):
    def __init__(self, line_num: LineNum, the_bytes: bytes):
        self.line_num = line_num
        self.bytes = the_bytes
        self.age = 0

    def visit_and_age(self) -> int:
        self.age += 1
        return self.age

