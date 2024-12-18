from typing import List, Tuple, Optional
from PyQt5.QtWidgets import (QDialog, QVBoxLayout,
                             QLabel, QPushButton,
                             QHBoxLayout, QWidget)


class CustomDialog(QDialog):
    """
    Класс для создания пользовательского диалогового окна
    с сообщением и настраиваемыми кнопками.

    :param parent: Родительский виджет (по умолчанию None).
    :param title: Заголовок диалогового окна (по умолчанию пустая
     строка).
    :param message: Сообщение для отображения в диалоговом окне
    (по умолчанию пустая строка).
    :param buttons: Список текстов кнопок и их соответствующих ролей.
        Каждая кнопка представлена в виде кортежа (текст, роль).

    :ivar layout: Вертикальное расположение для диалогового окна.
    :ivar label: Виджет метки для отображения сообщения.
    :ivar button_layout: Горизонтальное расположение для кнопок.
    :ivar buttons: Список объектов QPushButton, представляющих кнопки
    в диалоговом окне.
    """

    def __init__(self, parent: Optional[QWidget] = None,
                 title: str = '', message: str = '',
                 buttons: Optional[List[Tuple[str, int]]] = None):
        super().__init__(parent)

        if buttons is None:
            buttons = []

        self.setWindowTitle(title)

        self.layout = QVBoxLayout()

        self.label = QLabel(message)
        self.layout.addWidget(self.label)

        self.button_layout = QHBoxLayout()

        self.buttons = []
        for button_text, button_role in buttons:
            button = QPushButton(button_text)
            button.clicked.connect(lambda _, r=button_role: self.done(r))
            self.button_layout.addWidget(button)
            self.buttons.append(button)

        self.layout.addLayout(self.button_layout)
        self.setLayout(self.layout)
