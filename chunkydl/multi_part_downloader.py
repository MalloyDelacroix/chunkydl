import os
import shutil
import tempfile
from concurrent.futures import ThreadPoolExecutor
from queue import Queue

from .config import DownloadConfig
from .runner import Runner
from .utils import get_output, _download_actual


class MultiPartDownloader(Runner):

    """
    A class that breaks a large file download into multiple chunks, then downloads multiple chunks at the same time in
    order to increase the download speed.  The chunks are stored in a temporary directory during the download, and
    are then combined into a single file and the temporary directory deleted.

    Attributes:
        url (str): The url of the large file that is to be downloaded.
        output_path (str): The output path where the file parts will be downloaded.  May or may not include the final
            file name.  If a directory name is supplied in lieu of a file name, the name is taken from the url's
            basename, and the file parts (and finally the joined file) are saved at the directory path.
        output_dir (str): The path to the directory of the supplied output_path.  If the output_path included a file
            name, this is the separated path to the parent directory.  If it did not include a file name, this value is
            the same as the output_path variable.
        file_size (int): The size of the file, in bytes.  This value should be retrieved from the host server prior to
            instantiating this class.
        config (DownloadConfig): The download configuration object that holds the setup variables for this download.
        part_count (int): The number of parts to download.
        failed_parts (list): A list of failed download parts.
        executor (ThreadPoolExecutor): A thread pool executor to use for downloading file chunks.
        part_queue (Queue): A queue that holds download parts awaiting download.
        temp_path (str): The directory to save the downloaded file parts until they can be joined together.

    Args:
        url (str): The url of the large file that is to be downloaded.
        output_path (str): The output path where the file parts will be downloaded.  May or may not include the final
            file name.  If a directory name is supplied in lieu of a file name, the name is taken from the url's
            basename, and the file parts (and finally the joined file) are saved at the directory path.
        file_size (int): The size of the file, in bytes.  This value should be retrieved from the host server prior to
            instantiating this class.
        config (DownloadConfig): The download configuration object that holds the setup variables for this download.
    """

    def __init__(self, url: str, output_path: str, file_size: int, config: DownloadConfig):
        super().__init__()
        self.url = url
        self.output_path = output_path
        self.output_dir, self.output_name = get_output(output_path)
        self.file_size = file_size
        self.config = config
        self.part_count = 0
        self.failed_parts = 0
        self.executor = ThreadPoolExecutor(self.config.multi_part_thread_count)
        self.part_queue = Queue()
        self.temp_path = None

    def run(self) -> None:
        """
        Determines the number of chunks along with the start and end byte range of the file, then queues the download
        parts and starts the extractor which will download the parts.  After the extractor completes the downloads and
        shuts down, the join file method is called.
        """
        chunks = range(0, self.file_size, self.config.size_threshold)
        self.part_count = len(chunks)
        for part, start in enumerate(chunks):
            self.part_queue.put((part, start))
        self.part_queue.put(None)
        while self.continue_run:
            item = self.part_queue.get()
            if item is not None:
                part, start = item
                end = start + self.config.size_threshold - 1
                out_path = self.get_output_path(part)
                self.executor.submit(self.download_part, start=start, end=end, output_path=out_path)
            else:
                break
        self.executor.shutdown(wait=True)
        self.join_file()

    def download_part(self, start: int, end: int, output_path: str) -> None:
        """
        Handles the actual downloading of each file chunk based on the parameters supplied.
        Args:
            start: The start byte range to be downloaded.
            end: The end byte range to be downloaded.
            output_path: The path that the file part will be saved to.
        """
        headers = self.config.get_headers(range=f'bytes={start}-{end}')
        _download_actual(
            url=self.url,
            output_path=output_path,
            timeout=self.config.timeout,
            chunk_size=self.config.chunk_size,
            headers=headers,
            verify_ssl=self.config.verify_ssl,
        )

    def join_file(self) -> None:
        """
        Joins all the downloaded parts of the file into a single file, then deletes the temporary directory where
        the parts were stored during download.
        """
        with open(self.output_path, 'wb') as file:
            try:
                self.write_parts_to_file(file)
                self.remove_temp_path()
            except FileNotFoundError:
                if self.config.clean_up_on_fail:
                    self.remove_temp_path()
                print('Failed to join multi-part download_group')

    def write_parts_to_file(self, file):
        """
        Iterates through the saved temporary files reading the data from each one and writing it into the supplied open
        file to combine the parts into the single file.

        Args:
            file: An open writable file to which the file parts will be written.
        """
        for part in range(self.part_count):
            path = self.get_output_path(part)
            with open(path, 'wb') as part_file:
                file.write(part_file.read())

    def get_output_path(self, part: int):
        """
        Returns the temporary download path for a file part based on the part number supplied.  If a temporary directory
        does not exist, it will be created.

        Args:
            part: The sequential number of the part being downloaded.

        Returns:
            (str): The path where the file part will be saved to.
        """
        if self.temp_path is None:
            self.temp_path = tempfile.mkdtemp(dir=os.path.dirname(self.output_path))
        if self.output_name is None or self.output_name == '':
            self.output_name = os.path.basename(self.url)
        return os.path.join(self.temp_path, f'{self.output_name}.part-{part}')

    def remove_temp_path(self) -> None:
        """
        Remove the temporary directory and its contents after we are done with it and handle the error if there was an
        error making the directory, and it does not exist.
        """
        try:
            shutil.rmtree(self.temp_path)
        except FileNotFoundError:
            pass
