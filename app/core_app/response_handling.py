class ErrorHandling:
    default_message_en = "Something wrong!!"
    default_message_vi = "Có gì đó đang gặp vấn đề!!"

    def __init__(self, message_en, message_vi, code=None, lang="vi", **kwargs):
        self.code = code
        self.lang = lang
        self.kwargs = kwargs
        self.message_en = message_en
        self.message_vi = message_vi
        if lang == "en":
            self.message = message_en if message_en else self.default_message_en
        else:
            self.message = message_vi if message_vi else self.default_message_vi

    def to_representation(self):
        content = {
            "message": self.message,
            "vi": self.message_vi,
            "en": self.message_en,
            "code": self.code,
        }
        content = {**content, **self.kwargs}
        response = {"error": content}
        return response


class SuccessHandling:
    def __init__(self, message_vi, message_en, lang="vi", **kwargs):
        self.lang = lang
        self.message_en = message_en
        self.message_vi = message_vi
        if lang == "en":
            self.message = message_en
        else:
            self.message = message_vi
        self.kwargs = kwargs

    def to_representation(self):
        content = {
            "message": self.message,
            "vi": self.message_vi,
            "en": self.message_en,
        }
        content = {**content, **self.kwargs}
        response = {"success": content}
        return response
