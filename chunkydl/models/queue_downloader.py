import logging
from queue import Queue
from concurrent.futures import ThreadPoolExecutor, Future
from typing import Optional

from .download_config import DownloadConfig
from .data_models import DLGroup, Response
from chunkydl.runner import Runner, verify_run
from chunkydl.download import _download

logger = logging.getLogger(__name__)


class QueueDownloader(Runner):

    """
    A class that monitors an internal queue for files to be downloaded and, using a ThreadPoolExecutor, downloads
    several at the same time.  The number of simultaneous downloads will be determined by the corresponding value of the
    supplied config object.

    Attributes:
        config (DownloadConfig): The configuration object that will be used to determine the download parameters.
        _queue (Queue): The queue that stores pending downloads.
        executor (ThreadPoolExecutor): The executor that will be used to download files simultaneously.

    Args:
        config (DownloadConfig): The configuration object that will be used to determine the download parameters.
    """

    def __init__(self, config: DownloadConfig):
        super().__init__()
        self.config = config
        self._queue = Queue(maxsize=-1)
        self.executor = ThreadPoolExecutor(config.download_threads)
        self.results = []
        self.config.log_attributes('Queue downloader configured with following options')

    def add(self, item: Optional[DLGroup]) -> None:
        """
        Adds a new item to the download queue.

        Args:
            item (Optional[DLGroup]): The item that will be downloaded.
        """
        self._queue.put(item)
        logger.debug(f'Item added to download queue: {item}')

    def add_multiple(self, items: list[Optional[DLGroup]]) -> None:
        """
        Adds multiple items to the download queue.

        Args:
            items (list[Optional[DLGroup]]): A list of items to be added.
        """
        for item in items:
            self.add(item)

    def download_all(self) -> None:
        """
        Calls the run method in a more concise and user-friendly way.
        """
        self.run()

    def run(self) -> None:
        """
        Executes the download process for each item in the queue until the queue is empty.
        If an item is retrieved from the queue, the method calls 'download_group' to handle the download.
        If the queue is empty, the method stops the execution and shuts down the executor.
        """
        while self.continue_run:
            dl_group = self._queue.get()
            if dl_group is not None:
                future = self.executor.submit(self.download_group, dl_group=dl_group)
                future.add_done_callback(self.handle_future)
                logger.debug(f'Item submitted to executor: {dl_group}')
            else:
                logger.debug('Breaking out of download cycle')
                break
        self.executor.shutdown(wait=True)
        logger.info('Queue downloader shutdown')

    @verify_run
    def download_group(self, dl_group: DLGroup) -> Response:
        """
        Calls the actual download method with the values supplied in the dl_group.

        Args:
            dl_group (DLGroup): A DLGroup with values tha will be used for downloading a file.
                - url (str): The url of the file to be downloaded.
                - output_path (str): The path that the file will be saved to.
                - config (DownloadConfig): The configuration object that will be used to determine the download
                    parameters.
        """
        url, output_path, config = dl_group
        return _download(url, output_path, config)

    def handle_future(self, future: Future) -> None:
        """
        Gets the result from an executed future and adds it to the results list.

        Args:
            future (Future): The future as returned from submitting work to the thread pool executor.
        """
        self.results.append(future.result())
