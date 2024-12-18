from typing import Any, Callable, List

from view import UiMainWindow
from controller.cursor_manager import cursor_controller_for_hex, cursor_controller_for_text
from view.file_manager import open_file, save_file


def save_cursor(func: Callable) -> Callable:
    """
    Декоратор, сохраняющий позиции курсоров.

    :param func: Функция для декорирования.
    :type func: Callable
    :return: Декорированная функция.
    :rtype: Callable
    """
    def do(self, *args: Any) -> None:
        bytes_field_position = self.ui.bytes_field.textCursor().position()
        bytes_decryption_field_position = (
            self.ui.bytes_decryption_field.textCursor().position())

        func(self)
        self.show_file()

        bytes_field_cursor = self.ui.bytes_field.textCursor()
        bytes_field_cursor.setPosition(bytes_field_position)

        bytes_decryption_field_cursor = (
            self.ui.bytes_decryption_field.textCursor())
        bytes_decryption_field_cursor.setPosition(
            bytes_decryption_field_position)

        self.ui.bytes_field.setTextCursor(bytes_field_cursor)
        self.ui.bytes_decryption_field.setTextCursor(bytes_decryption_field_cursor)
    return do


def requires_research(func: Callable) -> Callable:
    """
    Декоратор, выполняющий действие и запускающий поиск.

    :param func: Функция для декорирования.
    :type func: Callable
    :return: Декорированная функция.
    :rtype: Callable
    """
    def foo(self, *args: Any) -> None:
        func(self, *args)
        try:
            self.searcher.start()
        except AttributeError:
            pass
    return foo


class HexEditor:
    """
    Класс редактора в шестнадцатеричном формате.
    """
    def __init__(self) -> None:
        self._16_base: List[str] = ['0', '1', '2', '3', '4', '5', '6', '7',
                                    '8', '9', 'a', 'b', 'c', 'd', 'e', 'f']

        self.ui = UiMainWindow()

        (self.ui.bytes_field.cursorPositionChanged.
         connect(lambda: cursor_controller_for_hex(self.ui)))
        (self.ui.bytes_decryption_field.cursorPositionChanged.
         connect(lambda: cursor_controller_for_text(self.ui)))
        self.ui.open_action.triggered.connect(self.dialog_to_open)
        self.ui.save_action.triggered.connect(self.dialog_to_save)
        self.ui.scroll_bar.valueChanged.connect(self.show_file)

        self.ui.hex_field_key_pres.connect(self.update_from_hex_position)
        self.ui.text_field_key_pres.connect(self.update_from_text_position)
        self.ui.hex_field_backspace.connect(self.backspace_event_from_hex)
        self.ui.text_field_backspace.connect(self.backspace_event_from_text)

        self.ui.multicursor_action.triggered.connect(self.add_cursor)
        self.ui.scroll_bar.valueChanged.connect(self.reset_cursors)
        self.ui.cursor_reset_action.triggered.connect(self.reset_cursors)

        self.ui.undo_action.triggered.connect(self.undo)
        self.ui.redo_action.triggered.connect(self.redo)

    def show_file(self) -> None:
        """
        Отображает содержимое файла.
        """
        try:
            self.bytes_buffer.update_data(self.ui.scroll_bar.value())
            self.ui.bytes_field.setText(self.bytes_buffer.to_hex())
            self.ui.bytes_decryption_field.setText(self.bytes_buffer.to_text())
            self.ui.count_units.setText(self.bytes_buffer.units_count())
            self.ui.count_tens.setText(self.bytes_buffer.tens_count())
            size = self.bytes_buffer.get_size() // 16
            if self.bytes_buffer.get_size() % 16 == 0:
                size -= 1
            self.ui.scroll_bar.setRange(0, size)
        except AttributeError:
            pass

    def add_cursor(self) -> None:
        """
        Добавляет курсор в поле с шестнадцатеричными данными.
        """
        self.bytes_buffer.cursors.append(
            self.ui.bytes_field.textCursor().position())

    def reset_cursors(self) -> None:
        """
        Сбрасывает курсоры.
        """
        try:
            self.bytes_buffer.cursors = []
        except Exception:
            pass

    def dialog_to_open(self) -> None:
        """
        Открывает диалоговое окно для выбора файла.
        """
        try:
            self.bytes_buffer = open_file()
            self.show_file()
            self.ui.scroll_bar.setValue(0)
            self.ui.bytes_field.setReadOnly(False)
            self.ui.bytes_decryption_field.setReadOnly(False)
        except FileNotFoundError:
            pass

    @requires_research
    @save_cursor
    def undo(self) -> None:
        """
        Отменяет последнее действие.
        """
        try:
            self.bytes_buffer.logger.undo()
        except AttributeError:
            pass

    @requires_research
    @save_cursor
    def redo(self) -> None:
        """
        Повторяет последнее отмененное действие.
        """
        try:
            self.bytes_buffer.logger.redo()
        except AttributeError:
            pass

    def dialog_to_save(self) -> None:
        """
        Открывает диалоговое окно для сохранения файла.
        """
        try:
            save_file(self.bytes_buffer)
            self.ui.bytes_field.clear()
            self.ui.bytes_field.setReadOnly(True)
            self.ui.bytes_decryption_field.clear()
            self.ui.bytes_decryption_field.setReadOnly(True)
            self.ui.count_tens.clear()
            self.ui.count_units.clear()
            delattr(self, 'bytes_buffer')
        except FileNotFoundError:
            pass
        except AttributeError:
            pass

    @requires_research
    def update_from_hex_position(self, cursor: Any, char: str) -> None:
        """
        Обновляет данные при изменении позиции курсора в шестнадцатеричном
        поле.

        :param cursor: Позиция курсора.
        :type cursor: Any
        :param char: Введенный символ.
        :type char: str
        """
        try:
            position = self.bytes_buffer.update_from_hex_position(
                cursor.position(), char, True)
            self.show_file()
            cursor.setPosition(position)
        except AttributeError:
            pass

    @requires_research
    def update_from_text_position(self, cursor: Any, char: str) -> None:
        """
        Обновляет данные при изменении позиции курсора в поле с текстовыми
        данными.

        :param cursor: Позиция курсора.
        :type cursor: Any
        :param char: Введенный символ.
        :type char: str
        """
        try:
            position = self.bytes_buffer.update_from_text_position(
                cursor.position(),
                char, True)
            self.show_file()
            cursor.setPosition(position)
        except AttributeError:
            pass

    @requires_research
    def backspace_event_from_text(self, cursor: Any) -> None:
        """
        Обрабатывает событие удаления символа из поля с текстовыми данными.

        :param cursor: Позиция курсора.
        :type cursor: Any
        """
        try:
            position = self.bytes_buffer.backspace_event_from_text(
                cursor.position())
            self.show_file()
            cursor.setPosition(position)
        except AttributeError:
            pass

    @requires_research
    def backspace_event_from_hex(self, cursor: Any) -> None:
        """
        Обрабатывает событие удаления символа из шестнадцатеричного поля.

        :param cursor: Позиция курсора.
        :type cursor: Any
        """
        try:
            position = self.bytes_buffer.backspace_event_from_hex(
                cursor.position())
            self.show_file()
            cursor.setPosition(position)
        except AttributeError:
            pass
