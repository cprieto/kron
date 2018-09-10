from typing import Optional, Union


class ServerError(Exception):
    def __init__(self, message: str, code: Optional[int], body: str):
        super().__init__(message)
        self.code = code
        self.body = body


class NotFoundError(Exception):
    def __init__(self, query: Union[str, int], entity: str = 'job'):
        self.query = query
        self.entity = entity


class ArgumentValidationError(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class AliasAlreadyExistsError(Exception):
    def __init__(self, alias: Optional[str] = None):
        self.alias = alias
