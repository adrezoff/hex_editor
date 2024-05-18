import json
import os


class Localization:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, '_initialized'):
            return
        self._initialized = True
        self.locale_dir = os.getcwd()
        self.language = self.load_language()
        self.translations = self.load_translations(self.language)

    def load_translations(self, language):
        file_path = os.path.join(self.locale_dir,
                                 f'resources/language/{language}.json')
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                translations = json.load(f)
                return translations
        except FileNotFoundError:
            print(f"Translation file '{file_path}' not found.")
            return {}

    def load_language(self):
        file_path = os.path.join(self.locale_dir, 'resources/language.json')

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                language = data.get('language')

                if isinstance(language, str):
                    return language
                else:
                    return 'english'
        except FileNotFoundError:
            return 'english'

    def set_language(self, language):
        self.language = language
        self.translations = self.load_translations(language)
        file_path = os.path.join(self.locale_dir, 'resources/language.json')
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump({'language': language}, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Ошибка сохранения языка: {e}")

    def localize(self, key):
        if key in self.translations:
            return self.translations[key]
        else:
            return f"Ошибка ключа: '{key}'"
