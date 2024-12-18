import sys
import os
from typing import Dict, List

from model.logging import Logger, LogRecord


class Buffer:
    """
    Класс для работы с данными в чанковом формате.

    :param file_name: Имя файла для работы с буфером.
    :type file_name: str
    """

    def __init__(self, file_name: str) -> None:
        self.row_count: int = 30
        self.chunk_size: int = 4194304
        self.len_byte = 3
        self.len_ascii_char = 16
        self.len_ascii_line = 17
        self.encoding: str = sys.getdefaultencoding()
        self._16_base: List[str] = ['0', '1', '2', '3', '4', '5', '6', '7',
                                    '8', '9', 'a', 'b', 'c', 'd', 'e', 'f']
        self.file_name: str = file_name
        self.file = open(file_name, 'br')
        self.file_size: int = os.path.getsize(file_name)
        self.extended_bytes: Dict[int, bytearray] = {}
        self.logger: Logger = Logger(self.extended_bytes)
        self.update_data(0)
        self.cursors: List[int] = []
        self.cursor_is_busy: bool = False

    def get_size(self) -> int:
        """
        Получает размер буфера, включая расширенные данные.

        :return: Размер буфера в байтах.
        :rtype: int
        """
        res: int = self.file_size
        for bytes_ in self.extended_bytes.values():
            res += len(bytes_) - 1
        return res

    def write_data(self, file) -> None:
        """
        Записывает данные буфера в файл.

        :param file: Файл для записи данных.
        :type file: file
        """
        self.file.seek(0)
        current_pos = 0
        extended_positions = sorted(self.extended_bytes.keys())

        for pos in extended_positions:
            if current_pos < pos:
                chunk_size = pos - current_pos
                file.write(self.file.read(chunk_size))
                current_pos += chunk_size

            file.write(self.extended_bytes[pos])
            current_pos += len(self.extended_bytes[pos])
            self.file.seek(current_pos)

        remaining_data = self.file.read()
        file.write(remaining_data)

    def update_data(self, shift: int) -> None:
        """
        Обновляет данные в соответствии с заданным сдвигом.

        :param shift: Сдвиг.
        :type shift: int
        """
        self.tens_offset = shift

        start = shift * self.len_ascii_char
        iter = 0
        self.shown = bytearray()
        self.byte_index = {}

        for i in sorted(self.extended_bytes.keys()):
            if i < start:
                if i + len(self.extended_bytes[i]) < start:
                    if len(self.extended_bytes[i]) == 0:
                        start += 1
                    elif len(self.extended_bytes[i]) > 1:
                        start -= len(self.extended_bytes[i]) - 1
                    self.byte_index[-1] = start - 1
                else:
                    shift = start - i
                    start = i + 1
                    for _ in self.extended_bytes[i][:shift]:
                        iter -= 1
                        self.byte_index[iter] = i
                    iter = 0
                    for byte in self.extended_bytes[i][shift:]:
                        self.byte_index[iter] = i
                        iter += 1
                        self.shown.append(byte)
                    break
            else:
                break

        self.file.seek(start)
        if self.file.tell() != 0:
            self.byte_index[-1] = self.file.tell() - 1

        while len(self.shown) < self.row_count * self.len_ascii_char:
            pos = self.file.tell()
            byte = self.file.read(1)
            if byte == b'':
                break
            if pos in self.extended_bytes:
                for byte in self.extended_bytes[pos]:
                    self.byte_index[iter] = pos
                    iter += 1
                    self.shown.append(byte)
            else:
                self.byte_index[iter] = pos
                iter += 1
                self.shown.append(byte[0])

    def get_position(self, index: int, shift: int) -> int:
        """
        Возвращает позицию байта в данных.

        :param index: Индекс байта.
        :type index: int
        :param shift: Сдвиг.
        :type shift: int
        :return: Позиция байта.
        :rtype: int
        """
        pos = 0
        for i in range(index):
            if i in self.extended_bytes:
                for j in self.extended_bytes[i]:
                    pos += 1
            else:
                pos += 1
        for i in range(shift):
            pos += 1
        return pos

    def update_from_hex_position(self, position: int,
                                 char: str, is_insert: bool) -> int:
        """
        Обновляет данные относительно позиции в шестнадцатеричном формате.

        :param position: Позиция в шестнадцатеричном формате.
        :type position: int
        :param char: Символ для обновления.
        :type char: str
        :param is_insert: Флаг вставки.
        :type is_insert: bool
        :return: Новая позиция.
        :rtype: int
        """
        if char in self._16_base:
            index = position // self.len_byte
            if position % self.len_byte == 0:
                if position != len(self.shown) * self.len_byte and is_insert:
                    new = char
                    new += self.shown[index:index + 1].hex()[1:]
                    self.add_byte(index, bytes.fromhex(new), True)
                else:
                    self.add_byte(index, bytes.fromhex(f'{char}0'), False)
                position += 1
            else:
                new = self.shown[index:index + 1].hex()[:1]
                new += char
                self.add_byte(index, bytes.fromhex(new), True)
                position += 2
            position = self.handle_multicursor(position, char, is_insert)
        return position

    def add_byte(self, index: int, byte: bytes, is_insert: bool) -> None:
        """
        Добавляет байт в данные на основе его положения.

        :param index: Индекс байта.
        :type index: int
        :param byte: Добавляемый байт.
        :type byte: bytes
        :param is_insert: Флаг вставки.
        :type is_insert: bool
        """
        if not is_insert:
            index -= 1
        try:
            if self.byte_index[index] in self.extended_bytes:
                shift = 0
                try:
                    while (self.byte_index[index - shift - 1]
                           == self.byte_index[index]):
                        shift += 1
                except KeyError:
                    pass
                log = LogRecord(self.byte_index[index],
                                self.extended_bytes[self.byte_index[index]],
                                byte, shift,
                                is_insert)
                if is_insert:
                    self.extended_bytes[self.byte_index[index]][shift] \
                        = byte[0]
                else:
                    (self.extended_bytes[self.byte_index[index]].
                     insert(shift + 1, byte[0]))
            else:
                new = bytearray()
                if is_insert:
                    log = LogRecord(self.byte_index[index],
                                    None, byte, 0, is_insert)
                elif index != -1:
                    new = bytearray(self.shown[index: index + 1])
                    log = LogRecord(self.byte_index[index],
                                    None, byte, 1, is_insert)
                else:
                    self.file.seek(self.byte_index[index])
                    new = bytearray(self.file.read(1))
                    log = LogRecord(self.byte_index[index],
                                    None, byte, 1, is_insert)
                new.append(byte[0])
                self.extended_bytes[self.byte_index[index]] = new
        except KeyError:
            if 0 not in self.extended_bytes:
                self.extended_bytes[0] = self.shown[0:1]
            log = LogRecord(0, self.extended_bytes[0], byte,
                            1, is_insert)
            self.extended_bytes[0].insert(0, byte[0])
        self.logger.add(log)

    def update_from_text_position(self, position: int,
                                  char: str, is_insert: bool) -> int:
        """
        Обновляет данные относительно позиции в текстовом формате.

        :param position: Позиция в текстовом формате.
        :type position: int
        :param char: Символ для обновления.
        :type char: str
        :param is_insert: Флаг вставки.
        :type is_insert: bool
        :return: Новая позиция.
        :rtype: int
        """
        if char.isalnum():
            index = position - (position // self.len_ascii_line)
            if (position != len(self.shown) +
                    (position // self.len_ascii_line) and is_insert):
                self.add_byte(index, char.encode(self.encoding), True)
            else:
                self.add_byte(index, char.encode(self.encoding), False)
            if position % self.len_ascii_line == 15:
                position += 1
            if index == len(self.shown):
                position += 1
            position += 1
        return position

    def delete_byte(self, index: int) -> None:
        """
        Удаляет байт из данных.

        :param index: Индекс байта.
        :type index: int
        """
        if self.byte_index[index] in self.extended_bytes:
            shift = 0
            try:
                while (self.byte_index[index - 1 - shift]
                       == self.byte_index[index]):
                    shift += 1
            except KeyError:
                pass
            log = LogRecord(self.byte_index[index],
                            self.extended_bytes[self.byte_index[index]],
                            b'', shift, True)
            try:
                self.extended_bytes[self.byte_index[index]].pop(shift)
            except IndexError:
                pass
        else:
            log = LogRecord(self.byte_index[index], None,
                            b'', 0, True)
            self.extended_bytes[self.byte_index[index]] = bytearray()
        self.logger.add(log)

    def backspace_event_from_text(self, position: int) -> int:
        """
        Выполняет действие "backspace" относительно позиции в
        текстовом формате.

        :param position: Позиция в текстовом формате.
        :type position: int
        :return: Новая позиция.
        :rtype: int
        """
        index = position - (position // self.len_ascii_line) - 1
        self.delete_byte(index)

        position -= 1
        if position % self.len_ascii_line == self.len_ascii_char:
            position -= 1
        return position

    def backspace_event_from_hex(self, position: int) -> int:
        """
        Выполняет действие "backspace" относительно позиции в
        шестнадцатеричном формате.

        :param position: Позиция в шестнадцатеричном формате.
        :type position: int
        :return: Новая позиция.
        :rtype: int
        """
        if position % self.len_byte == 0 and position != 0:
            index = position // self.len_byte - 1
            self.delete_byte(index)
            position -= self.len_byte
            position = self.handle_multicursor(position, '',
                                               True)
        else:
            position = self.handle_multicursor(position, '',
                                               False)

        return position

    def tens_count(self) -> str:
        """
        Возвращает строку с десятками в шестнадцатеричном формате.

        :return: Строка с десятками.
        :rtype: str
        """
        end = self.tens_offset + len(self.shown) // self.len_ascii_char + 1
        return ''.join([str(hex(x))[2:].zfill(7) +
                        '0\n' for x in range(self.tens_offset, end)])

    def units_count(self) -> str:
        """
        Возвращает строку с единицами в шестнадцатеричном формате.

        :return: Строка с единицами.
        :rtype: str
        """
        return ' '.join([f'0{digit}' for digit in self._16_base])

    def to_hex(self) -> str:
        """
        Возвращает данные в шестнадцатеричном формате.

        :return: Данные в шестнадцатеричном формате.
        :rtype: str
        """
        _hex = self.shown.hex()
        hex_list = [_hex[i:i + 2] for i in range(0, len(_hex), 2)]

        if len(hex_list) % self.len_ascii_char != 0:
            for i in range(0, self.len_ascii_char -
                              len(hex_list) % self.len_ascii_char):
                hex_list.append('')

        return ('\n'.join(
            [' '.join([hex_list[j] for j in
                       range(i, i + self.len_ascii_char)])
             for i in range(0, len(hex_list),
                            self.len_ascii_char)]).rstrip() + ' ')

    def to_text(self) -> str:
        """
        Возвращает данные в текстовом формате.

        :return: Данные в текстовом формате.
        :rtype: str
        """
        text = ''.join([self.char_decrypt(i)
                        for i in range(len(self.shown))])

        res = '\n'.join([text[i:i + self.len_ascii_char] for i
                         in range(0, len(text) - len(text)
                                  % self.len_ascii_char,
                                  self.len_ascii_char)])

        return (res + f'\n{text[len(text) - len(text) 
                                % self.len_ascii_char:]}').lstrip('\n')

    def char_decrypt(self, index: int) -> str:
        """
        Переводит байты в символы.

        :param index: Индекс байта.
        :type index: int
        :return: Символ.
        :rtype: str
        """
        res = ''
        if self.shown[index] != '':
            if self.shown[index] < 20:
                res += '.'
            else:
                try:
                    res += self.shown[index:index + 1].decode(self.encoding)
                except UnicodeDecodeError:
                    res += '.'
        return res

    def handle_multicursor(self, position: int,
                           char: str, is_insert_or_is_deleted: bool) -> int:
        """
        Управляет несколькими курсорами.

        :param position: Текущая позиция.
        :type position: int
        :param char: Символ для обновления.
        :type char: str
        :param is_insert_or_is_deleted: Флаг вставки или удаления.
        :type is_insert_or_is_deleted: bool
        :return: Новая позиция.
        :rtype: int
        """
        if not self.cursor_is_busy:
            self.cursor_is_busy = True
            self.cursors = list(set(self.cursors))
            self.cursors.sort()
            if char == '':
                if position % self.len_byte == 0 and is_insert_or_is_deleted:
                    for i in range(len(self.cursors)):
                        if self.cursors[i] > position + self.len_byte:
                            self.cursors[i] -= self.len_byte
                for i in range(len(self.cursors) - 1, -1, -1):
                    if self.cursors[i] % self.len_byte == 0:
                        if (position + self.len_byte > self.cursors[i] != 0
                                and self.cursors != 0):
                            position -= self.len_byte
                        self.cursors[i] = (
                            self.backspace_event_from_hex(self.cursors[i]))
            else:
                if (not is_insert_or_is_deleted
                        and (position - 1) % self.len_byte == 0):
                    for i in range(len(self.cursors)):
                        if self.cursors[i] > position - self.len_byte:
                            self.cursors[i] += self.len_byte
                offset = 0
                for i in range(len(self.cursors)):
                    self.cursors[i] = (offset +
                                       self.update_from_hex_position(
                                           self.cursors[i],
                                           char,
                                           is_insert_or_is_deleted))
                    if (not is_insert_or_is_deleted and (self.cursors[i] - 1)
                            % self.len_byte == 0):
                        offset += self.len_byte
                        if self.cursors[i] < position - self.len_byte:
                            position += self.len_byte
            self.cursor_is_busy = False
        return position
