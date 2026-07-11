class InvalidCursorException(Exception):
    def __init__(self, pointer_name: str, index_accessed: int) -> None:
        self.pointer_name = pointer_name
        self.index_accessed = index_accessed

        super().__init__(self.pointer_name, self.index_accessed)

    def __str__(self) -> str:
        return f"The {self.pointer_name} went out of bound. Tried to access index {self.index_accessed}"


class NullPointerException(Exception):
    def __init__(self, error_message):
        self.error_message = error_message
        super().__init__(error_message)

    def __str__(self) -> str:
        return self.error_message
