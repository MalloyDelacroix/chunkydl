from queue import Queue
from concurrent.futures import ThreadPoolExecutor

from .config import DownloadConfig
from .runner import Runner, verify_run
from .download import _download


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
        self.executor = ThreadPoolExecutor(config.file_download_thread_count)

    def add(self, item):
        """
        Adds a new item to the download queue.

        Args:
            item: The item that will be downloaded.
        """
        self._queue.put(item)

    def download_all(self):
        """
        Calls the run method in a more concise and user-friendly way.
        """
        self.run()

    def run(self):
        """
        Executes the download process for each item in the queue until the queue is empty.
        If an item is retrieved from the queue, the method calls 'download_group' to handle the download.
        If the queue is empty, the method stops the execution and shuts down the executor.
        """
        while self.continue_run:
            dl_group = self._queue.get()
            if dl_group is not None:
                print(f'Submitted: {dl_group.url}')
                self.executor.submit(self.download_group, dl_group=dl_group)
            else:
                print('Stopping download queue')
                break
        self.executor.shutdown(wait=True)

    @verify_run
    def download_group(self, dl_group):
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
        _download(url, output_path, config)
