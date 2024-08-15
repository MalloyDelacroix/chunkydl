import unittest
from unittest.mock import patch, ANY

from chunkydl import download, download_list, DownloadConfig, QueueDownloader


class TestDownload(unittest.TestCase):

    @patch('chunkydl.api._download')
    def test_download_accepts_download_config_object_correctly(self, mock_download):
        config = DownloadConfig()
        download('http://test-site.com/path/to/file', '/path/to/file/', config=config)

        mock_download.assert_called_with(ANY, ANY, config)

    @patch('chunkydl.api._download')
    def test_download_overrides_kwargs_with_config_when_config_is_provided(self, mock_download):
        size = 1024 * 1024 * 200
        wrong_size = 1024 * 1024 * 1000
        config = DownloadConfig(size_threshold=size)
        download(
            'http://test-site.com/path/to/file',
            '/path/to/file/',
            config=config,
            size_threshold=wrong_size
        )

        mock_download.assert_called_with(ANY, ANY, config)


class TestDownloadList(unittest.TestCase):

    @patch('chunkydl.api.QueueDownloader')
    def test_download_list_accepts_download_config_object_correctly(self, mock_downloader):
        config = DownloadConfig()
        url_list = [
            'http://example.com/path/to/file_one.mp4',
            'http://example.com/path/to/file_two.mp4',
            'http://example_site_two.com/path/to/file_three.mp4',
        ]
        download_list(url_list, '/path/to/file/', config=config)

        mock_downloader.assert_called_with(config=config)

    @patch('chunkydl.api.QueueDownloader')
    def test_download_list_overrides_kwargs_with_config_when_config_is_provided(self, mock_downloader):
        size = 1024 * 1024 * 200
        wrong_size = 1024 * 1024 * 1000
        config = DownloadConfig(size_threshold=size)
        url_list = [
            'http://example.com/path/to/file_one.mp4',
            'http://example.com/path/to/file_two.mp4',
            'http://example_site_two.com/path/to/file_three.mp4',
        ]
        download_list(
            url_list,
            '/path/to/file/',
            config=config,
            size_threshold=wrong_size
        )

        mock_downloader.assert_called_with(config=config)
