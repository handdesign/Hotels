from googletrans import Translator


class TranslateCity:

    @classmethod
    def translate_city(cls, city: str):
        translator = Translator()
        result = translator.translate(city.lower(), dest='en')

        return result.text
