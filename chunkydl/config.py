import logging


logger = logging.getLogger(__name__)


class DownloadConfig:

    """
    Mainly a data class that stores values used for configuring the exact behavior of a download session such as the
    multipart size threshold, multiple download thread count, and additional configuration options.

    Attributes:
        default_headers (dict): Dictionary of default headers to be included in all requests.
    """

    default_headers = {'Accept': '*/*'}

    def __init__(self, **kwargs):
        """
        Instantiates a DownloadConfig object.

        Args:
            **kwargs:
                timout (int): The timout time, in seconds, before a request is abandoned.  Default is 10.
                retries (int): The number of times a request will be retried.  Default is 3.
                chunk_size (int): The size of a download chunk in bytes that will be downloaded from a streamed request.
                    This is the smallest downloadable unit used for each download request.  See "size_threshold" below
                    for multipart chunk size.  Default is 1MB.
                additional_headers (dict): A dict of headers that will be added to the default headers provided by this
                    class.
                complete_headers (dict): Overwrites the default headers.  If supplied, these will be the only headers
                    used for each request.
                verify_ssl (bool): Whether to verify the SSL certificate on each request.  Default is True.
                size_threshold (int): The size, in bytes, after which the multipart downloader will be used to download
                    a file.  This size limit is also used for determining the size of each larger chunk that will be
                    downloaded by each thread of the multipart downloader, and therefor the number of chunks the file
                    will be broken into for download.  Default is 100MB.
                file_download_thread_count (int): The number of download threads that will be used to download a file.
                multi_part_thread_count (int): The number of download threads that will be used to download a file with
                    the multipart downloader.
                run_perpetual (bool): Indicates if the download loop should stay open after the initial queue is empty.
                    True will keep the download thread alive and the queue active so that more downloads can be added to
                    the download queue.  Default is False.
                clean_up_on_fail (bool): Indicates if the multiple parts of a file downloaded with the multipart
                    downloader will be deleted if some part of the multipart download fails.  Default is False.
        """
        self.timeout = kwargs.get('timeout', 10)
        self.retries = kwargs.get('retries', 3)
        self.chunk_size = kwargs.get('chunk_size', 1024 * 1024)
        self._additional_headers = kwargs.get('additional_headers', None)
        self._complete_headers = kwargs.get('headers', None)
        self.verify_ssl = kwargs.get('verify_ssl', True)
        self.size_threshold = kwargs.get('size_threshold', 1024 * 1024 * 100)
        self.file_download_thread_count = kwargs.get('file_download_thread_count', 4)
        self.multi_part_thread_count = kwargs.get('multi_part_thread_count', 4)
        self.run_perpetual = kwargs.get('run_perpetual', False)
        self.clean_up_on_fail = kwargs.get('clean_up_on_fail', False)

    @property
    def headers(self) -> dict:
        """
        Returns the headers as configured by the kwargs supplied to the class initializer.

        Returns:
            The headers as configured by the kwargs supplied to the class initializer.
        """
        if self._complete_headers is not None:
            return self._complete_headers
        headers = self.default_headers.copy()
        if self._additional_headers is not None:
            for key, value in self._additional_headers.items():
                headers[key] = value
        return headers

    @headers.setter
    def headers(self, headers: dict):
        self._complete_headers = headers

    def get_headers(self, **kwargs) -> dict:
        """
        A method that returns the headers as configured by the kwargs supplied to the class initializer, but that allows
        the addition of extra headers at call time by way of kwargs.

        Args:
            **kwargs: Any extra headers that should be included in the headers returned from this class.

        Returns:
            dict: A dict of headers used for a request.
        """
        headers = self.headers.copy()
        headers.update(kwargs)
        return headers

    def log_attributes(self, message):
        logger.debug(
            f'{message}: '
            f'timeout: {self.timeout}, '
            f'retries: {self.retries}, '
            f'chunk_size: {self.chunk_size}, '
            f'headers: {self.headers}, '
            f'verify_ssl: {self.verify_ssl}, '
            f'size_threshold: {self.size_threshold}, '
            f'file_download_thread_count: {self.file_download_thread_count}, '
            f'multi_part_thread_count: {self.multi_part_thread_count}, '
            f'run_perpetual: {self.run_perpetual}, '
            f'clean_up_on_fail: {self.clean_up_on_fail}'
        )
