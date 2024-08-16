import unittest
from unittest.mock import patch, mock_open, MagicMock

import requests.exceptions
import urllib3
from http.client import HTTPMessage

from chunkydl import DownloadConfig
from chunkydl.core import download_actual
from chunkydl.exceptions import RequestFailedException


class TestDownloadActual(unittest.TestCase):

    @patch('requests.Session.get')
    @patch('builtins.open', new_callable=mock_open)
    def test_successful_download(self, mock_file, mock_get):
        """
        Tests that the download function calls the requests library with the correct information, and returns the
        correct value.
        """
        url = "http://example.com/file"
        output_path = "output.txt"
        config = DownloadConfig()

        mock_response = MagicMock(status_code=200, url=url)
        mock_get.return_value = mock_response

        result = download_actual(url, output_path, config=config)
        mock_get.assert_called_with(url, stream=True, timeout=config.timeout, headers=config.headers)
        self.assertEqual(url, result.url)
        self.assertEqual(200, result.status_code)

        mock_file.assert_called()

    @patch('requests.Session.get')
    def test_non_200_206_status_code(self, mock_get):
        """
        Handles unsuccessful responses by raising RequestFailedException with the correct values.
        """
        url = "http://example.com/file"
        output_path = "output.txt"
        config = DownloadConfig()

        mock_response = MagicMock(status_code=404)
        mock_get.return_value = mock_response

        with self.assertRaises(RequestFailedException) as context:
            download_actual(url, output_path, config=config)

        self.assertEqual(context.exception.status_code, 404)
        self.assertEqual(context.exception.url, url)

    def test_empty_url(self, ):
        output_path = "output.txt"
        config = DownloadConfig()

        with self.assertRaises(ValueError):
            download_actual('', output_path, config)

        with self.assertRaises(ValueError):
            download_actual(None, output_path, config)

    @patch('requests.Session.get')
    def test_retries_correctly_on_approved_status_codes(self, mock_get):
        url = "http://example.com/file"
        output_path = "output.txt"
        config = DownloadConfig(retries=3, retry_status_codes=[503], backoff_factor=1)

        mock_get.size_effect = [
            requests.exceptions.ConnectionError('Failed first attempt'),
            requests.exceptions.ConnectionError('Failed second attempt'),
            MagicMock(status_code=200),
        ]

        # with self.assertRaises(RequestFailedException):
        result = download_actual(url, output_path, config=config)
        self.assertEqual(3, mock_get.call_count)


    # TODO: test that additional kwargs supplied to download_actual are used in the request header
