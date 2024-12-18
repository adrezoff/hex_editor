import json
import os
from typing import Dict, Any


class Localization:
    """
    Синглтон для управления локализацией в приложении.
    """

    _instance = None

    def __new__(cls) -> 'Localization':
        """
        Создает новый экземпляр Localization, если он не существует.
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """
        Инициализирует экземпляр Localization.
        """
        if hasattr(self, '_initialized'):
            return
        self._initialized = True
        self.locale_dir: str = os.getcwd()
        self.language: str = self.load_language()
        self.translations: Dict[str, Any] = (
            self.load_translations(self.language))

    def load_translations(self, language: str) -> Dict[str, Any]:
        """
        Загружает переводы для указанного языка.

        :param language: Код языка.
        :type language: str
        :return: Словарь с переводами.
        :rtype: dict
        """
        file_path: str = os.path.join(self.locale_dir,
                                      f'resources/language/{language}.json')
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                translations: Dict[str, Any] = json.load(f)
                return translations
        except FileNotFoundError:
            print(f"Файл перевода '{file_path}' не найден.")
            return {}

    def load_language(self) -> str:
        """
        Загружает текущий язык.

        :return: Текущий язык.
        :rtype: str
        """
        file_path: str = os.path.join(self.locale_dir,
                                      'resources/language.json')

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data: Dict[str, Any] = json.load(f)
                language: str = data.get('language')

                if isinstance(language, str):
                    return language
                else:
                    return 'english'
        except FileNotFoundError:
            return 'english'

    def set_language(self, language: str) -> None:
        """
        Устанавливает текущий язык.

        :param language: Название.
        :type language: str
        """
        self.language = language
        self.translations = self.load_translations(language)
        file_path: str = os.path.join(self.locale_dir,
                                      'resources/language.json')
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump({'language': language},
                          f,
                          ensure_ascii=False,
                          indent=4)
        except Exception as e:
            print(f"Ошибка сохранения языка: {e}")

    def localize(self, key: str) -> str:
        """
        Получение значения по ключу.

        :param key: Ключ.
        :type key: str
        """
        if key in self.translations:
            return self.translations[key]
        else:
            return f"Ошибка ключа: '{key}'"
