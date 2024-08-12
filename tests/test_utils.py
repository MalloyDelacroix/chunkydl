import os
import unittest
from unittest.mock import patch, MagicMock
import requests

from chunkydl.utils import get_output, get_name_from_url, _download_actual
from chunkydl.exceptions import RequestFailedException


class TestGetOutput(unittest.TestCase):

    @patch('os.path.isdir')
    def test_returns_directory_path_and_none_for_directory_when_directory_path_is_supplied(self, mock_isdir):
        """
        Tests that a tuple of (directory_path, None) is returned when a directory path without file name is supplied.
        """
        mock_isdir.return_value = True
        output_path = "/path/to/directory"
        expected_result = (output_path, None)
        result = get_output(output_path)
        self.assertEqual(expected_result, result)

    @patch('os.path.isdir')
    def test_returns_parent_directory_and_file_name_when_path_with_file_name_is_supplied(self, mock_isdir):
        mock_isdir.return_value = False
        dir_path = '/path/to/directory'
        file_name = 'filename.mp4'
        output_path = os.path.join(dir_path, file_name)
        expected_result = (dir_path, file_name)
        result = get_output(output_path)
        self.assertEqual(expected_result, result)

    @patch('os.path.isdir')
    def test_handles_empty_string_as_output_path(self, mock_isdir):
        """
        Tests that empty strings are handled correctly.
        """
        mock_isdir.return_value = False
        output_path = ""
        expected_result = ("", "")
        self.assertEqual(get_output(output_path), expected_result)

    @patch('os.path.isdir')
    def test_handles_output_path_with_special_characters(self, mock_isdir):
        """
        Tests that output paths with special characters are handled correctly.
        """
        mock_isdir.return_value = False
        output_path = "/path/to/special!@#$%^&*()_+file.txt"
        expected_result = ("/path/to", "special!@#$%^&*()_+file.txt")
        self.assertEqual(get_output(output_path), expected_result)


class TestGetNameFromURL(unittest.TestCase):

    def test_extracts_filename_from_standard_url(self):
        """
        Tests that a standard URL is extracted correctly.
        """
        url = "http://example.com/path/to/file.txt"
        expected = "file.txt"
        result = get_name_from_url(url)
        self.assertEqual(result, expected)

    def test_handles_urls_with_no_path_component(self):
        """
        Tests that urls with no path component are handled correctly.
        """
        url = "http://example.com"
        expected = ""
        result = get_name_from_url(url)
        self.assertEqual(result, expected)

    def test_processes_urls_with_trailing_slashes_correctly(self):
        """
        Tests that urls with trailing slashes are handled correctly.
        """
        url = "http://example.com/path/to/directory/"
        expected = ""
        result = get_name_from_url(url)
        self.assertEqual(result, expected)


class TestDownloadActual(unittest.TestCase):

    @patch('requests.get')
    def test_successful_download(self, mock_get):
        """
        Tests that the download function calls the requests library with the correct information, and returns the
        correct value.
        """
        url = "http://example.com/file"
        output_path = "output.txt"
        timeout = 10
        headers = {}
        chunk_size = 1024
        verify_ssl = False

        mock_response = MagicMock(status_code=200)
        mock_get.return_value = mock_response

        result = _download_actual(url, output_path, timeout, headers, chunk_size, verify_ssl)
        mock_get.assert_called_with(url, stream=True, timeout=timeout, headers=headers, verify=verify_ssl)
        self.assertTrue(result)

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
        verify_ssl = False

        mock_response = MagicMock(status_code=404)
        mock_get.return_value = mock_response

        with self.assertRaises(RequestFailedException) as context:
            _download_actual(url, output_path, timeout, headers, chunk_size, verify_ssl)

        self.assertEqual(context.exception.status_code, 404)
        self.assertEqual(context.exception.url, url)
