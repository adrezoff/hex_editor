import sys
from PyQt5 import QtWidgets
from controller.controller import HexEditor

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    hex_editor = HexEditor()
    sys.exit(app.exec_())
