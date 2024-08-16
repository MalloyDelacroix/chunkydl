import unittest
from unittest.mock import Mock
import time

from chunkydl import DownloadConfig
from chunkydl.models.queue_downloader import QueueDownloader


class TestRun(unittest.TestCase):

    def test_executor_is_shutdown_when_retrieving_none_from_queue(self):
        config = DownloadConfig()
        mock_executor = Mock()
        downloader = QueueDownloader(config=config)
        downloader.executor = mock_executor
        downloader.add(('url', 'path', config))
        downloader.add(('url2', 'path2', config))
        downloader.add(None)
        downloader.run()
        self.assertEqual(2, mock_executor.submit.call_count)
        mock_executor.shutdown.assert_called()

    def test_executor_is_called_with_correct_values(self):
        config = DownloadConfig()
        mock_executor = Mock()
        downloader = QueueDownloader(config=config)
        downloader.executor = mock_executor
        downloader.add(('url', 'path', config))
        downloader.add(None)
        downloader.run()
        mock_executor.submit.assert_called_once_with(downloader.download_group, dl_group=('url', 'path', config))
        mock_executor.shutdown.assert_called_with(wait=True)

    def test_calling_downloaders_stop_method_stops_download_without_none_being_added_to_queue(self):
        config = DownloadConfig()
        mock_executor = Mock()
        downloader = QueueDownloader(config=config)
        downloader.executor = mock_executor
        downloader.start()
        downloader.add(('url', 'path', config))
        downloader.add(('url2', 'path2', config))
        downloader.stop()
        time.sleep(0.002)  # Allow downloader thread enough time to close the loop
        mock_executor.shutdown.assert_called_with(wait=True)
        self.assertFalse(downloader.continue_run)
