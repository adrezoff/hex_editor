from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout


class CustomDialog(QDialog):
    def __init__(self, parent=None, title='', message='', buttons=None):
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
