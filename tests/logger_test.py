import unittest

from model import Logger, LogRecord


class TestLogger(unittest.TestCase):
    def setUp(self):
        self.extended_bytes = {}
        self.logger = Logger(self.extended_bytes)

    def test_add_byte(self):
        log_record = LogRecord(0, bytearray(), bytearray([0x01]),
                               0, True)
        self.logger.add(log_record)
        self.logger.extended_bytes[0] = bytearray([0x01])
        self.assertEqual(self.extended_bytes, {0: bytearray([0x01])})

    def test_undo_insert(self):
        log_record = LogRecord(0, bytearray(), bytearray([0x01]),
                               0, True)
        self.logger.add(log_record)
        self.logger.extended_bytes[0] = bytearray([0x01])
        self.logger.undo()
        self.assertEqual(self.extended_bytes, {})

    def test_undo_delete(self):
        log_record = LogRecord(0, bytearray([0x01]), bytearray(),
                               0, False)
        self.logger.add(log_record)
        self.logger.extended_bytes = {0: bytearray([0x01])}
        self.logger.undo()
        self.assertEqual(self.extended_bytes, {})

    def test_redo_insert(self):
        log_record = LogRecord(0, bytearray(), bytearray([0x01]),
                               0, True)
        self.logger.add(log_record)
        self.logger.extended_bytes[0] = bytearray([0x01])
        self.logger.undo()
        self.logger.redo()
        self.assertEqual(self.extended_bytes, {0: bytearray([0x01])})

    def test_redo_delete(self):
        log_record = LogRecord(0, bytearray([0x01]), bytearray(),
                               0, False)
        self.logger.add(log_record)
        self.logger.extended_bytes = {0: bytearray([0x01])}
        self.logger.undo()
        self.logger.redo()
        self.assertEqual(self.extended_bytes, {})

    def test_multiple_add_and_undo(self):
        log_record_1 = LogRecord(1, bytearray(), bytearray([0x02]),
                                 0, True)
        log_record_2 = LogRecord(2, bytearray(), bytearray([0x03]),
                                 0, True)
        self.logger.add(log_record_1)
        self.logger.add(log_record_2)
        self.extended_bytes[1] = bytearray([0x02])
        self.extended_bytes[2] = bytearray([0x03])
        self.assertEqual(self.extended_bytes, {1: bytearray([0x02]),
                                               2: bytearray([0x03])})
        self.logger.undo()
        self.logger.undo()
        self.assertEqual(self.extended_bytes, {})

    def test_multiple_add_and_redo(self):
        log_record_1 = LogRecord(1, bytearray(), bytearray([0x02]),
                                 0, True)
        log_record_2 = LogRecord(2, bytearray(), bytearray([0x03]),
                                 0, True)
        self.logger.add(log_record_1)
        self.logger.add(log_record_2)
        self.extended_bytes[1] = bytearray([0x02])
        self.extended_bytes[2] = bytearray([0x03])
        self.logger.undo()
        self.logger.undo()
        self.logger.redo()
        self.logger.redo()
        self.assertEqual(self.extended_bytes, {1: bytearray([0x02]),
                                               2: bytearray([0x03])})


if __name__ == '__main__':
    unittest.main()