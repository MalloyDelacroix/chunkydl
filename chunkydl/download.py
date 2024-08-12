import os.path
import requests

from .config import DownloadConfig
from .exceptions import RequestFailedException
from .utils import get_output, get_name_from_url, _download_actual
from .multi_part_downloader import MultiPartDownloader


def _download(url: str, output_path: str, config: DownloadConfig) -> None:
    """
    Downloads a file from the given URL to the specified output path based on the provided configuration.
    If the file size exceeds the threshold defined in the configuration, it uses the MultiPartDownloader.

    Args:
        url (str): The URL of the file to download.
        output_path (str): The path where the downloaded file will be saved.  If the output path ends is a directory,
            the file name is taken from the server.  If the server does not provide the file name, the basename  of the
            url is used.
        config (dict): The DownloadConfig object containing download configuration settings.
    """
    response = requests.head(url, timeout=config.timeout)
    if response.status_code != 200:
        raise RequestFailedException(url=url, status_code=response.status_code, message=response.reason)
    dir_path, name = get_output(output_path)
    if not name:
        name = response.headers.get('Content-Disposition', get_name_from_url(url))
    output = str(os.path.join(dir_path, name))
    size = int(response.headers.get('content-length', 0))
    if size > config.size_threshold:
        multi_part_downloader = MultiPartDownloader(url, output, file_size=size, config=config)
        multi_part_downloader.run()
    else:
        _download_actual(
            url=url,
            output_path=output,
            timeout=config.timeout,
            chunk_size=config.chunk_size,
            headers=config.headers,
            verify_ssl=config.verify_ssl,
        )
