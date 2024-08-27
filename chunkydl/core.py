import requests
from requests.adapters import HTTPAdapter, Retry

from .exceptions import RequestFailedException
from .utils import make_response
from .models.download_config import DownloadConfig
from .models.data_models import Response


def download_actual(url: str, output_path: str, config: DownloadConfig, **kwargs) -> Response:
    """
    Download a file from a given URL and save it to the specified output path.

    Args:
        url (str): The URL of the file to download.
        output_path (str): The path where the downloaded file will be saved.
        config (DownloadConfig): The download configuration object that holds the setup variables for this download.
        **kwargs: Additional keyword arguments to pass to the requests.get function.

    Returns:
        Response: A response object containing useful information from the response returned by the get request made in
        this method.
    """
    session = get_request_session(config)
    response = session.get(url, stream=True, timeout=config.timeout, headers=config.headers, **kwargs)
    if response.status_code != 200 and response.status_code != 206:
        raise RequestFailedException(url, response.status_code, response.reason)
    with open(output_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=config.chunk_size):
            if chunk:
                f.write(chunk)
    return make_response(response)


def get_request_session(config: DownloadConfig) -> requests.Session:
    """
    Configures the session that will be used to make requests.

    Args:
        config (DownloadConfig): The download configuration object that holds the setup variables for this download.:
    """
    session = requests.Session()
    retry_strategy = get_retry_strategy(config)
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session


def get_retry_strategy(config: DownloadConfig) -> Retry:
    """
    Configures the retry strategy used by a request session.
    Args:
        config (DownloadConfig): The download configuration object that holds the setup variables for this download.:
    """
    return Retry(
        total=config.retries,
        status_forcelist=config.retry_status_codes,
        backoff_factor=config.backoff_factor,
        allowed_methods=['HEAD', 'GET']
    )
