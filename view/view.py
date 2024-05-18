from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox, QDialog

from model.cursor_manager import cursor_correcting_for_hex
from view.localization import Localization
from utils import CustomDialog


class UiMainWindow(QtWidgets.QMainWindow):
    hex_field_key_pres = QtCore.pyqtSignal(QtGui.QTextCursor, str)
    text_field_key_pres = QtCore.pyqtSignal(QtGui.QTextCursor, str)
    hex_field_backspace = QtCore.pyqtSignal(QtGui.QTextCursor)
    text_field_backspace = QtCore.pyqtSignal(QtGui.QTextCursor)

    def __init__(self):
        super().__init__()
        self.resize(640, 480)
        self.setup_ui()
        self.show()

    def setup_ui(self):
        thickening = 40
        font = QtGui.QFont("PT Mono", 12)
        font_metrics = QtGui.QFontMetrics(font)
        char_width = font_metrics.horizontalAdvance('a')
        char_height = font_metrics.height()

        self.central_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.central_widget)

        self.locale = Localization()

        spacer = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)

        self.bytes_field = QtWidgets.QTextEdit(self.central_widget)
        self.bytes_field.setFont(font)
        self.bytes_field.setMinimumWidth(char_width * 16 * 3 + thickening)
        self.bytes_field.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.bytes_field.setReadOnly(True)
        self.bytes_field.keyPressEvent = self.hex_key_event
        self.bytes_field.wheelEvent = lambda _: None

        self.count_tens = QtWidgets.QTextEdit(self.central_widget)
        self.count_tens.setFixedWidth(char_width * 9 + thickening)
        self.count_tens.setFont(font)
        self.count_tens.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.count_tens.setDisabled(True)

        self.bytes_decryption_field = QtWidgets.QTextEdit(self.central_widget)
        self.bytes_decryption_field.setFixedWidth(char_width * 17 + thickening)
        self.bytes_decryption_field.setFont(font)
        self.bytes_decryption_field.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.bytes_decryption_field.setWordWrapMode(QtGui.QTextOption.NoWrap)
        self.bytes_decryption_field.setReadOnly(True)
        self.bytes_decryption_field.keyPressEvent = self.text_key_event
        self.bytes_decryption_field.wheelEvent = lambda _: None

        self.count_units = QtWidgets.QTextBrowser(self.central_widget)
        self.count_units.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.count_units.setMaximumHeight(char_height + 10)
        self.count_units.setFont(font)
        self.count_units.setDisabled(True)

        self.lable = QtWidgets.QLabel()
        self.lable.setFont(QtGui.QFont("PT Mono", 12, QtGui.QFont.Bold))
        font.setBold(True)
        self.lable.setFont(font)

        self.scroll_bar = QtWidgets.QScrollBar()
        self.scroll_bar.setRange(0, 0)

        self.layout = QtWidgets.QGridLayout()
        self.layout.addItem(spacer, 1, 0, 1, 1)
        self.layout.addWidget(self.bytes_field, 1, 2, 1, 1)
        self.layout.addWidget(self.count_tens, 1, 1, 1, 1)
        self.layout.addWidget(self.bytes_decryption_field, 1, 3, 1, 1)
        self.layout.addWidget(self.count_units, 0, 2, 1, 1)
        self.layout.addWidget(self.lable, 0, 1, 1, 1)
        self.layout.addItem(spacer, 1, 4, 1, 1)

        self.upper_layout = QtWidgets.QHBoxLayout()

        self.main_layout = QtWidgets.QHBoxLayout()
        self.main_layout.addLayout(self.layout)
        self.main_layout.addWidget(self.scroll_bar)

        self.global_layout = QtWidgets.QVBoxLayout(self.central_widget)
        self.global_layout.addLayout(self.upper_layout)
        self.global_layout.addLayout(self.main_layout)

        self.menubar = QtWidgets.QMenuBar(self)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 640, 22))

        self.file_menu = QtWidgets.QMenu(self.menubar)
        self.actions_menu = QtWidgets.QMenu(self.menubar)

        self.window_menu = QtWidgets.QMenu(self.menubar)
        self.language_menu = QtWidgets.QMenu(self.window_menu)

        self.language_action_en = QtWidgets.QAction("English", self)
        self.language_action_ru = QtWidgets.QAction("Русский", self)

        self.window_menu.addMenu(self.language_menu)

        self.undo_action = QtWidgets.QAction(self)
        self.redo_action = QtWidgets.QAction(self)
        self.setMenuBar(self.menubar)

        self.open_action = QtWidgets.QAction(self)
        self.save_action = QtWidgets.QAction(self)

        self.file_menu.addAction(self.open_action)
        self.file_menu.addAction(self.save_action)
        self.actions_menu.addAction(self.undo_action)
        self.actions_menu.addAction(self.redo_action)
        self.menubar.addAction(self.file_menu.menuAction())
        self.menubar.addAction(self.actions_menu.menuAction())
        self.language_menu.addAction(self.language_action_en)
        self.language_menu.addAction(self.language_action_ru)

        self.menubar.addAction(self.window_menu.menuAction())

        self.set_titles()

        self.multicursor_action = QtWidgets.QAction("Multicursor", self.bytes_field)
        self.multicursor_action.setShortcut(QtGui.QKeySequence("Ctrl+Q"))
        self.bytes_field.addAction(self.multicursor_action)

        self.cursor_reset_action = QtWidgets.QAction("Multicursor", self.bytes_field)
        self.cursor_reset_action.setShortcut(QtGui.QKeySequence("Ctrl+R"))
        self.bytes_field.addAction(self.cursor_reset_action)

        self.language_action_en.triggered.connect(lambda: self.change_language('english'))
        self.language_action_ru.triggered.connect(lambda: self.change_language('russian'))

    def set_titles(self):
        self.setWindowTitle(self.locale.localize('title'))
        self.file_menu.setTitle(self.locale.localize('file'))
        self.open_action.setText(self.locale.localize('open'))
        self.save_action.setText(self.locale.localize('save'))
        self.actions_menu.setTitle(self.locale.localize('action'))
        self.undo_action.setText(self.locale.localize('action.undo'))
        self.redo_action.setText(self.locale.localize('action.redo'))
        self.window_menu.setTitle(self.locale.localize('window'))
        self.language_menu.setTitle(self.locale.localize('language'))
        self.lable.setText(self.locale.localize('offset'))

    def change_language(self, language_code):
        self.locale.set_language(language_code)
        self.set_titles()

    def hex_key_event(self, event):
        cursor = self.bytes_field.textCursor()
        if event.key() == QtCore.Qt.Key_Left:
            cursor_correcting_for_hex(cursor)
            cursor.movePosition(cursor.Left, cursor.MoveAnchor, 3)
        elif event.key() == QtCore.Qt.Key_Right:
            cursor_correcting_for_hex(cursor)
            cursor.movePosition(cursor.Right, cursor.MoveAnchor, 3)
        elif event.key() == QtCore.Qt.Key_Up:
            cursor_correcting_for_hex(cursor)
            cursor.movePosition(cursor.Up, cursor.MoveAnchor, 1)
        elif event.key() == QtCore.Qt.Key_Down:
            cursor_correcting_for_hex(cursor)
            cursor.movePosition(cursor.Down, cursor.MoveAnchor, 1)
        elif event.key() == QtCore.Qt.Key_Backspace:
            self.hex_field_backspace.emit(cursor)
        else:
            self.hex_field_key_pres.emit(cursor, event.text())
        self.bytes_field.setTextCursor(cursor)

    def text_key_event(self, event):
        cursor = self.bytes_decryption_field.textCursor()
        if event.key() == QtCore.Qt.Key_Left:
            cursor.movePosition(cursor.Left, cursor.MoveAnchor, 1)
            if cursor.position() % 17 == 16:
                cursor.movePosition(cursor.Left, cursor.MoveAnchor, 1)
        elif event.key() == QtCore.Qt.Key_Right:
            cursor.movePosition(cursor.Right, cursor.MoveAnchor, 1)
        elif event.key() == QtCore.Qt.Key_Up:
            cursor.movePosition(cursor.Up, cursor.MoveAnchor, 1)
        elif event.key() == QtCore.Qt.Key_Down:
            cursor.movePosition(cursor.Down, cursor.MoveAnchor, 1)
        elif event.key() == QtCore.Qt.Key_Backspace:
            self.text_field_backspace.emit(cursor)
        else:
            self.text_field_key_pres.emit(cursor, event.text())
        self.bytes_decryption_field.setTextCursor(cursor)

    def closeEvent(self, event):
        title = self.locale.localize('confirm_exit_title')
        message = self.locale.localize('confirm_exit_message')
        yes = self.locale.localize('yes')
        no = self.locale.localize('no')

        dialog = CustomDialog(self, title, message, [(yes, QDialog.Accepted), (no, QDialog.Rejected)])
        result = dialog.exec_()

        if result == QDialog.Accepted:
            event.accept()
        else:
            event.ignore()
