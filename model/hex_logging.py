import copy


class LogRecord:
    def __init__(self, index, old_extend, new_byte, shift, is_insert):
        self.index = index
        self.old_extend = copy.copy(old_extend)
        self.new_byte = new_byte
        self.shift = shift
        self.is_insert = is_insert


class Logger:
    def __init__(self, extended_bytes):
        self.extended_bytes = extended_bytes
        self.undo_stack = []
        self.redo_stack = []

    # Добавление записи
    def add(self, log_record):
        self.undo_stack.append(log_record)
        self.redo_stack.clear()

    def undo(self):
        try:
            log = self.undo_stack.pop()
            if log.old_extend is not None:
                self.extended_bytes[log.index] = log.old_extend
            else:
                self.extended_bytes.pop(log.index)
            self.redo_stack.append(log)
        except IndexError:
            pass

    def redo(self):
        try:
            log = self.redo_stack.pop()
            if log.new_byte == b'':
                if log.shift == 0:
                    if log.index - 1 in self.extended_bytes:
                        log = LogRecord(log.index - 1,
                                        self.extended_bytes[log.index - 1],
                                        log.new_byte,
                                        len(self.extended_bytes[log.index - 1])
                                        - 1, log.is_insert)
                        self.extended_bytes[log.index][log.shift] =\
                            log.new_byte
                    else:
                        log = LogRecord(log.index - 1, None,
                                        log.new_byte, 0, log.is_insert)
                        if log.index == -1:
                            raise IndexError
                        self.extended_bytes[log.index] = bytearray()
                else:
                    log = LogRecord(log.index,
                                    self.extended_bytes[log.index],
                                    log.new_byte, log.shift - 1, log.is_insert)
                    self.extended_bytes[log.index].pop(log.shift)
            else:
                if len(self.extended_bytes[log.index]) == log.shift + 1:
                    if log.is_insert:
                        if log.index + 1 in self.extended_bytes:
                            log = LogRecord(log.index + 1,
                                            self.extended_bytes[log.index + 1],
                                            log.new_byte, 0, log.is_insert)
                            self.extended_bytes[log.index][log.shift] =\
                                log.new_byte[0]
                        else:
                            log = LogRecord(log.index + 1,
                                            None,
                                            log.new_byte, 0, log.is_insert)
                            self.extended_bytes[log.index] =\
                                bytearray(log.new_byte)
                    else:
                        log = LogRecord(log.index,
                                        self.extended_bytes[log.index],
                                        log.new_byte, log.shift + 1,
                                        log.is_insert)
                        self.extended_bytes[log.index].append(log.new_byte[0])
                else:
                    log = LogRecord(log.index, self.extended_bytes[log.index],
                                    log.new_byte, log.shift + 1, log.is_insert)
                    if log.is_insert:
                        self.extended_bytes[log.index][log.shift] =\
                            log.new_byte[0]
                    else:
                        self.extended_bytes[log.index].insert(log.shift,
                                                              log.new_byte[0])
            self.undo_stack.append(log)
        except IndexError:
            pass
