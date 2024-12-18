from PyQt5 import QtWidgets
from model.model import Buffer
from typing import Union


def open_file() -> Union[Buffer, None]:
    """
    Открывает файл с помощью стандартного диалога открытия файла и
    возвращает его содержимое в виде объекта Buffer.

    :return: Объект Buffer, содержащий данные файла, либо None, если
    пользователь не выбрал файл.
    :rtype: Union[Buffer, None]
    """
    file_name = QtWidgets.QFileDialog.getOpenFileName()[0]
    if file_name:
        return Buffer(file_name)
    return None


def save_file(buffer: Buffer) -> None:
    """
    Сохраняет данные из объекта Buffer в файл с помощью стандартного
     диалога сохранения файла.

    :param buffer: Объект Buffer, содержащий данные для сохранения.
    :type buffer: Buffer
    """
    file_name = QtWidgets.QFileDialog.getSaveFileName()[0]
    if file_name:
        with open(file_name, 'wb') as file:
            buffer.write_data(file)
