import copy
from typing import Dict, List, Union


class LogRecord:
    """
    Запись журнала изменений.

    :param index: Индекс, к которому
    относится изменение.
    :type index: int
    :param old_extend: Старое значение для
    расширения данных.
    :type old_extend: bytearray
    :param new_byte: Новый байт.
    :type new_byte: bytes
    :param shift: Сдвиг.
    :type shift: int
    :param is_insert: Флаг, указывающий на вставку
    (True) или удаление (False).
    :type is_insert: bool
    """

    def __init__(self, index: int,
                 old_extend: Union[bytearray, None],
                 new_byte: bytes,
                 shift: int,
                 is_insert: bool) -> None:
        self.index: int = index
        self.old_extend: bytearray = copy.copy(old_extend)
        self.new_byte: bytes = new_byte
        self.shift: int = shift
        self.is_insert: bool = is_insert


class Logger:
    """
    Журнал изменений.

    :param extended_bytes: Расширенные байты.
    :type extended_bytes: Dict[int, bytearray]
    """

    def __init__(self, extended_bytes: Dict[int, bytearray]) -> None:
        self.extended_bytes: Dict[int, bytearray] = extended_bytes
        self.undo_stack: List[LogRecord] = []
        self.redo_stack: List[LogRecord] = []

    def add(self, log_record: LogRecord) -> None:
        """
        Добавляет запись в журнал.

        :param log_record: Запись журнала.
        :type log_record: LogRecord
        """
        self.undo_stack.append(log_record)
        self.redo_stack.clear()

    def undo(self) -> None:
        """Отменяет последнее действие."""
        if not self.undo_stack:
            return
        log: LogRecord = self.undo_stack.pop()
        if log.is_insert:
            if log.index in self.extended_bytes:
                self.extended_bytes[log.index].pop(log.shift)
                if not self.extended_bytes[log.index]:
                    del self.extended_bytes[log.index]
        else:
            if log.index in self.extended_bytes:
                (self.extended_bytes[log.index].
                 insert(log.shift, log.old_extend[log.shift]))
            else:
                self.extended_bytes[log.index] = (
                    bytearray([log.old_extend[log.shift]]))
        self.redo_stack.append(log)

    def redo(self) -> None:
        """Повторяет отмененное действие."""
        if not self.redo_stack:
            return
        log: LogRecord = self.redo_stack.pop()
        if log.is_insert:
            if log.index in self.extended_bytes:
                self.extended_bytes[log.index].insert(log.shift,
                                                      log.new_byte[0])
            else:
                self.extended_bytes[log.index] = bytearray([log.new_byte[0]])
        else:
            self.extended_bytes[log.index].pop(log.shift)
            if not self.extended_bytes[log.index]:
                del self.extended_bytes[log.index]
        self.undo_stack.append(log)
