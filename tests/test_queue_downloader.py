import unittest
from unittest.mock import patch, Mock
import time

from chunkydl import DownloadConfig
from chunkydl.queue_downloader import QueueDownloader


class MyTestCase(unittest.TestCase):

    def test_executor_is_shutdown_when_retrieving_none_from_queue(self):
        config = DownloadConfig()
        mock_executor = Mock()
        downloader = QueueDownloader(config=config)
        downloader.executor = mock_executor
        downloader.add('test_one')
        downloader.add('test_two')
        downloader.add(None)
        downloader.run()
        self.assertEqual(2, mock_executor.submit.call_count)
        mock_executor.shutdown.assert_called()

    def test_calling_downloaders_stop_method_stops_download_without_none_being_added_to_queue(self):
        config = DownloadConfig()
        mock_executor = Mock()
        downloader = QueueDownloader(config=config)
        downloader.executor = mock_executor
        downloader.start()
        downloader.add('test_one')
        downloader.add('test_two')
        downloader.stop()
        time.sleep(0.002)  # Allow downloader thread enough time to close the loop
        mock_executor.shutdown.assert_called()
        self.assertFalse(downloader.continue_run)
