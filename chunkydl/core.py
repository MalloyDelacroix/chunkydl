import requests

from .exceptions import RequestFailedException
from .utils import make_response


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
        Response: A response object containing useful information from the response returned by the get request made in
        this method.
    """
    response = requests.get(url, stream=True, timeout=timeout, headers=headers, **kwargs)
    if response.status_code != 200 and response.status_code != 206:
        raise RequestFailedException(url, response.status_code, response.reason)
    with open(output_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=chunk_size):
            if chunk:
                f.write(chunk)
    return make_response(response)
