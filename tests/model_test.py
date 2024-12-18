import unittest
import tempfile
import os
from model.model import Buffer


class TestBuffer(unittest.TestCase):
    def setUp(self):
        self.test_file = tempfile.NamedTemporaryFile(delete=False)
        self.test_file.write(b'0123456789abcdef')
        self.test_file.close()
        self.buffer = Buffer(self.test_file.name)

    def tearDown(self):
        os.remove(self.test_file.name)

    def test_initialization(self):
        self.assertEqual(self.buffer.get_size(), 16)
        self.assertEqual(self.buffer.shown, b'0123456789abcdef')

    def test_add_byte(self):
        self.buffer.add_byte(0, b'\x01', True)
        self.assertEqual(self.buffer.extended_bytes, {0: bytearray([1])})

    def test_delete_byte(self):
        self.buffer.add_byte(0, b'\x01', True)
        self.buffer.delete_byte(0)
        self.assertEqual(self.buffer.extended_bytes, {0: bytearray()})

    def test_undo_add(self):
        self.buffer.add_byte(0, b'\x01', True)
        self.buffer.logger.undo()
        self.assertEqual(self.buffer.extended_bytes, {})

    def test_redo_add(self):
        self.buffer.add_byte(0, b'\x01', True)
        self.buffer.logger.undo()
        self.buffer.logger.redo()
        self.assertEqual(self.buffer.extended_bytes, {0: bytearray([1])})

    def test_backspace_event_from_text(self):
        self.buffer.add_byte(0, b'\x01', True)
        position = self.buffer.backspace_event_from_text(1)
        self.assertEqual(self.buffer.extended_bytes, {0: bytearray()})
        self.assertEqual(position, 0)

    def test_backspace_event_from_hex(self):
        self.buffer.update_from_hex_position(0, 'f', True)
        position = self.buffer.backspace_event_from_hex(3)
        self.assertEqual(self.buffer.extended_bytes, {0: bytearray()})
        self.assertEqual(position, 0)

    def test_write_data(self):
        temp_output = tempfile.NamedTemporaryFile(delete=False)
        self.buffer.write_data(temp_output)
        temp_output.close()
        with open(temp_output.name, 'rb') as f:
            data = f.read()
        os.remove(temp_output.name)
        self.assertEqual(data, b'0123456789abcdef')

    def test_get_position(self):
        pos = self.buffer.get_position(1, 0)
        self.assertEqual(pos, 1)
        pos = self.buffer.get_position(1, 1)
        self.assertEqual(pos, 2)


if __name__ == '__main__':
    unittest.main()
