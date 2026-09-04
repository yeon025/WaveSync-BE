from app.exceptions.error_code import ErrorCode


class CustomException(Exception):
    def __init__(self, error_code: ErrorCode):
        self.status_code = error_code.value[0]
        self.code = error_code.value[1]
        self.message = error_code.value[2]
