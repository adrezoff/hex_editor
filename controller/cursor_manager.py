def cursor_controller_for_text(ui):
    """
    Контролирует курсор, чтобы он вёл себя правильно в поле
    с переводом.

    :param ui: Объект пользовательского интерфейса.
    :type ui: QtWidgets.QMainWindow
    """
    cursor = ui.bytes_decryption_field.textCursor()
    if cursor.position() % 17 == 16:
        cursor.movePosition(cursor.Right, cursor.MoveAnchor, 1)
        ui.bytes_decryption_field.setTextCursor(cursor)


def cursor_controller_for_hex(ui):
    """
    Контролирует курсор, чтобы он вёл себя правильно в поле
    с шестнадцатеричными данными.

    :param ui: Объект пользовательского интерфейса.
    :type ui: QtWidgets.QMainWindow
    """
    cursor = ui.bytes_field.textCursor()
    position = cursor.position()
    text = ui.bytes_field.toPlainText()
    if position != len(text) and text[position] == ' ':
        cursor.movePosition(cursor.Right, cursor.MoveAnchor, 1)
        ui.bytes_field.setTextCursor(cursor)


def cursor_correcting_for_hex(cursor):
    """
    Корректирует курсор для перемещения через стрелки.

    :param cursor: Курсор текста.
    :type cursor: QTextCursor
    """
    if (cursor.position() - 1) % 3 == 0:
        cursor.movePosition(cursor.Left, cursor.MoveAnchor, 1)
