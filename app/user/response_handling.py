from rest_framework import status


class ErrorHandling:
    def __init__(self, message, code, type=None, lang="vi", **kwargs):
        self.code = code
        self.type = type
        self.lang = lang
        self.kwargs = kwargs
        message_split = message.split("/")
        if len(message_split) == 1:
            self.message = message
        elif len(message_split) == 2:
            if self.lang == "en":
                self.message = message_split[1].strip()
            else:
                self.message = message_split[0].strip()
        else:
            self.message = None

    def to_representation(self):
        content = {"message": self.message, "type": self.type, "code": self.code}
        content = {**content, **self.kwargs}
        r = {"error": content}
        return r


class SuccessHandling:
    def __init__(self, message, code, type=None, lang="vi", **kwargs):
        self.code = code
        self.type = type
        self.lang = lang
        self.kwargs = kwargs
        message_split = message.split("/")
        if len(message_split) == 1:
            self.message = message
        elif len(message_split) == 2:
            if self.lang == "en":
                self.message = message_split[1].strip()
            else:
                self.message = message_split[0].strip()
        else:
            self.message = None

    def to_representation(self):
        content = {"message": self.message, "type": self.type, "code": self.code}
        content = {**content, **self.kwargs}
        r = {"success": content}
        return r
