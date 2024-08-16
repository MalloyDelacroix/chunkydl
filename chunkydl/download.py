import os
import logging
import requests

from .models.download_config import DownloadConfig
from .exceptions import RequestFailedException
from .core import download_actual
from .utils import get_output, get_name_from_url
from .models.data_models import Response
from .models.multi_part_downloader import MultiPartDownloader


logger = logging.getLogger(__name__)


def _download(url: str, output_path: str, config: DownloadConfig) -> Response:
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
    logger.debug(f'Request to {url} successful')
    dir_path, name = get_output(output_path)
    if not name:
        name = get_name_from_url(url)
        logger.debug(f'Name taken from url: {name}')
    output = str(os.path.join(dir_path, name))
    size = int(response.headers.get('content-length', 0))
    logger.debug(f'{url} file size: {size} bytes')
    if size > config.size_threshold:
        logger.debug(f'File size exceeds threshold of {config.size_threshold}, multi-part downloader is being used')
        multi_part_downloader = MultiPartDownloader(url, output, file_size=size, config=config)
        multi_part_downloader.run()
    else:
        logger.debug(f'File size under threshold of {config.size_threshold}, downloading file in one part')
        return download_actual(
            url=url,
            output_path=output,
            config=config
        )
