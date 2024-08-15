from typing import Union

from .config import DownloadConfig
from .download import _download
from .utils import DLGroup, Response
from .queue_downloader import QueueDownloader


def download(url: str, output_path: str, **kwargs) -> Response:
    """
    Downloads a file from the url to the output_path using the configuration variables that are supplied.

    Args:
        url (str): The url of the file that will be downloaded.
        output_path (str): The path where the file will be saved.  The path may be a directory or a file path.  If a
            file path is supplied, it will be used to name the file.  If only a directory is supplied, the file will be
            saved in the directory and the file's name will be taken from the base name of the url.
        **kwargs: Download configuration variables.
            timout (int): The timout time, in seconds, before a request is abandoned.  Default is 10.
            retries (int): The number of times a request will be retried.  Default is 3.
            chunk_size (int): The size of a download chunk in bytes that will be downloaded from a streamed request.
                This is the smallest downloadable unit used for each download request.  See "size_threshold" below
                for multipart chunk size.  Default is 1MB.
            additional_headers (dict): A dict of headers that will be added to the default headers provided by this
                class.
            complete_headers (dict): Overwrites the default headers.  If supplied, these will be the only headers
                used for each request.
            size_threshold (int): The size, in bytes, after which the multipart downloader will be used to download
                a file.  This size limit is also used for determining the size of each larger chunk that will be
                downloaded by each thread of the multipart downloader, and therefor the number of chunks the file
                will be broken into for download.  Default is 100MB.
            multi_part_thread_count (int): The number of download threads that will be used to download a file with
                the multipart downloader.
            run_perpetual (bool): Indicates if the download loop should stay open after the initial queue is empty.
                True will keep the download thread alive and the queue active so that more downloads can be added to
                the download queue.  Default is False.
            clean_up_on_fail (bool): Indicates if the multiple parts of a file downloaded with the multipart
                downloader will be deleted if some part of the multipart download fails.  Default is False.
    """
    config = DownloadConfig(**kwargs)
    return _download(url, output_path, config)


def download_list(urls: list[Union[str, DLGroup]], output_dir: str, **kwargs) -> list[Response]:
    """
    Downloads a list of urls to the specified output directory using the configuration variables that are supplied.
    Multiple files will be downloaded simultaneously depending on the supplied configuration variables.

    Args:
        urls: A list of urls in string form to be downloaded, or a list of DLGroup objects which hold urls to be
            downloaded. Supplying a list of strings will download all files to the directory supplied using the
            configuration variables supplied.  If individual configuration is required for each url, a list of DLGroup
            objects can be supplied which specify the url, output path, and configuration variables for each file.
        output_dir: The directory where the files will be saved.  The path should be to a directory.  If a path to a
            file is supplied, the file's containing directory will be used.
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
    config = DownloadConfig(**kwargs)
    downloader = QueueDownloader(config=config)
    for url in urls:
        if isinstance(url, str):
            group = DLGroup(url, output_dir, config)
            downloader.add(group)
        else:
            downloader.add(url)
    downloader.add(None)
    downloader.run()
    return downloader.results
