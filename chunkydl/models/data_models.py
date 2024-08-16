from datetime import timedelta
from typing import NamedTuple, Dict

from .download_config import DownloadConfig


class DLGroup(NamedTuple):
    """
    A NamedTuple representing data that will be used for downloading a file and specifying its output path and
    individual configuration options.

    Attributes:
        url (str): The URL of the downloadable file.
        output_path (str): The path where the file will be downloaded.
        config (DownloadConfig): A DownloadConfig object that specifies the download configuration for this particular
            file.
    """
    url: str
    output_path: str
    config: DownloadConfig


class Response(NamedTuple):

    """
    A NamedTuple that holds data as returned from a request.  The main content of the original response is not kept, but
    attributes that may be of use to the user are stored here and returned in a convenience wrapper.

    Attributes:
        url (str): The URL that the request was made to.
        headers (Dict[str, str]): The headers returned by the original response.
        status_code (int): The HTTP status code of the original response.
        elapsed (timedelta): The elapsed time between sending the request and receiving the original response.
    """

    url: str
    headers: Dict[str, str]
    status_code: int
    elapsed: timedelta
