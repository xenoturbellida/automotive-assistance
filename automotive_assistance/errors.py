class YandexAPIError(Exception):
    def __init__(self, message="Yandex returns error"):
        super().__init__(message)


class FolderIdNotSpecified(Exception):
    def __init__(self, message="No folder id in environment"):
        super().__init__(message)
