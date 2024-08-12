import os
from urllib.parse import urlparse
from typing import NamedTuple
import requests

from .exceptions import RequestFailedException
from .config import DownloadConfig


# DLGroup = namedtuple('DLGroup', ['url', 'output_path', 'config'])
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


def get_output(output_path: str) -> tuple:
    """
    Gets the output path for the downloaded file based on the supplied output path.  If the path is a directory, only
    the directory path will be used and the file will be named the same as is returned by the server.  If a full file
    path is supplied with a filename, that filename will be used for the downloaded file.

    Args:
        output_path (str): The output path supplied to the download_group method.

    Returns:
        tuple: A tuple of which the first value is the download_group directory and the second value is the filename
            if supplied or None if the supplied path is a directory.
    """
    if os.path.isdir(output_path):
        return output_path, None
    dir_path = os.path.dirname(output_path)
    name = os.path.basename(output_path)
    return dir_path, name


def get_name_from_url(url: str) -> str:
    """
    Extracts the path name from a url, then returns only the name portion of that path.

    Args:
        url (str): The url for which a name is to be extracted.

    Returns:
        str: The name of the file at the supplied url.
    """
    o = urlparse(url)
    return os.path.basename(o.path)


def _download_actual(
    url: str, output_path: str, timeout: int, headers: dict, chunk_size: int, verify_ssl: bool = False, **kwargs
) -> bool:
    """
    Download a file from a given URL and save it to the specified output path.

    Args:
        url (str): The URL of the file to download.
        output_path (str): The path where the downloaded file will be saved.
        timeout (int): The timeout for the request in seconds.
        headers (dict): The headers to include in the request.
        chunk_size (int): The size of each chunk to download.
        verify_ssl (bool, optional): Whether to verify SSL certificates (default is False).
        **kwargs: Additional keyword arguments to pass to the requests.get function.

    Returns:
        bool: True if the download is successful, False otherwise.
    """
    response = requests.get(url, stream=True, timeout=timeout, headers=headers, verify=verify_ssl, **kwargs)
    if response.status_code != 200 and response.status_code != 206:
        raise RequestFailedException(url, response.status_code, response.reason)
    with open(output_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=chunk_size):
            if chunk:
                f.write(chunk)
    return True
