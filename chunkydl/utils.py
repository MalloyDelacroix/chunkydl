import os
from typing import Union
from urllib.parse import urlparse
import requests

from .exceptions import RequestFailedException, OutputPathRequiredException
from .models.data_models import DLGroup, Response


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
    url: str, output_path: str, timeout: int, headers: dict, chunk_size: int, **kwargs
) -> requests.Response:
    """
    Download a file from a given URL and save it to the specified output path.

    Args:
        url (str): The URL of the file to download.
        output_path (str): The path where the downloaded file will be saved.
        timeout (int): The timeout for the request in seconds.
        headers (dict): The headers to include in the request.
        chunk_size (int): The size of each chunk to download.
        **kwargs: Additional keyword arguments to pass to the requests.get function.

    Returns:
        chunkydl.models.data_models.Response: A response object containing useful information from the response returned by the get request made in
        this method.
    """
    if output_path is None or output_path == '':
        raise OutputPathRequiredException()
    response = requests.get(url, stream=True, timeout=timeout, headers=headers, **kwargs)
    if response.status_code != 200 and response.status_code != 206:
        raise RequestFailedException(url, response.status_code, response.reason)
    with open(output_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=chunk_size):
            if chunk:
                f.write(chunk)
    return make_response(response)


def make_response(response: requests.Response) -> Response:
    """
    Takes a requests.Response object and extracts the pertinent information from it, returning it as a Response object.

    Args:
        response (requests.Response): A requests.Response object as returned from a request.

    Returns:
        Response: A Response object containing pertinent information from the supplied requests.Response.
    """
    headers = dict(response.headers)
    return Response(
        url=response.url,
        headers=headers,
        status_code=response.status_code,
        elapsed=response.elapsed,
    )


def convert_urls(urls: list[Union[str, DLGroup]], output_dir, config) -> list[DLGroup]:
    """
    Verifies that the supplied urls are DLGroup objects and if not, converts them.

    Args:
        urls (list[Union[str, DLGroup]]): The list of urls to check or convert.:
        output_dir (str): The output directory where the downloaded files will be saved.
        config (DLConfig): The DLConfig object used to configure the downloaded files.

    Returns:
        list[DLGroup]: A list of DLGroup objects with necessary download parameters.
    """
    groups = []
    for url in urls:
        if isinstance(url, str):
            group = DLGroup(url=url, output_path=output_dir, config=config)
            groups.append(group)
        else:
            groups.append(url)
    return groups
