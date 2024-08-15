

class RequestFailedException(Exception):

    """
    An exception raised when a request fails.

    Attributes:
        url (str): The url that on which the request failed.
        status_code (int): The status code of the failed request.
        message (str): The exception message.

    Args:
        url (str): The url that on which the request failed.
        status_code (int): The status code of the failed request.
        message (str): The exception message.
        *args: Any additional arguments that should be shown to the user that has been generated by the request failure.
    """

    def __init__(self, url: str, status_code: int, message: str, *args):
        self.url = url
        self.status_code = status_code
        self.message = message
        super().__init__(f'Request to {url} failed with satus code {status_code}: {message}', *args)


class OutputPathRequiredException(Exception):

    """
    An exception raised when an output path is not supplied for a download.

    Args:
        *args: Any additional arguments that should be shown to the user regarding the exception.
    """

    def __init__(self, *args):
        super().__init__(f'No output path supplied for download.  All downloads need at least a directory path in '
                         f'which to save downloaded files.', *args)
