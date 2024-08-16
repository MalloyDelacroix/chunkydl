import unittest
from unittest.mock import patch, mock_open, MagicMock

from chunkydl.core import _download_actual
from chunkydl.exceptions import RequestFailedException


class TestDownloadActual(unittest.TestCase):

    @patch('requests.get')
    @patch('builtins.open', new_callable=mock_open)
    def test_successful_download(self, mock_file, mock_get):
        """
        Tests that the download function calls the requests library with the correct information, and returns the
        correct value.
        """
        url = "http://example.com/file"
        output_path = "output.txt"
        timeout = 10
        headers = {}
        chunk_size = 1024

        mock_response = MagicMock(status_code=200, url=url)
        mock_get.return_value = mock_response

        result = _download_actual(url, output_path, timeout, headers, chunk_size)
        mock_get.assert_called_with(url, stream=True, timeout=timeout, headers=headers)
        self.assertEqual(url, result.url)
        self.assertEqual(200, result.status_code)

        mock_file.assert_called()

    @patch('requests.get')
    def test_non_200_206_status_code(self, mock_get):
        """
        Handles unsuccessful responses by raising RequestFailedException with the correct values.
        """
        url = "http://example.com/file"
        output_path = "output.txt"
        timeout = 10
        headers = {}
        chunk_size = 1024

        mock_response = MagicMock(status_code=404)
        mock_get.return_value = mock_response

        with self.assertRaises(RequestFailedException) as context:
            _download_actual(url, output_path, timeout, headers, chunk_size)

        self.assertEqual(context.exception.status_code, 404)
        self.assertEqual(context.exception.url, url)

    def test_empty_url(self, ):
        output_path = "output.txt"
        timeout = 10
        headers = {}
        chunk_size = 1024

        with self.assertRaises(ValueError):
            _download_actual('', output_path, timeout, headers, chunk_size)

        with self.assertRaises(ValueError):
            _download_actual(None, output_path, timeout, headers, chunk_size)

    # TODO: test that additional kwargs supplied to _download_actual are used in the request header
