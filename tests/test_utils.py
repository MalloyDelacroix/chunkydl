import os
import unittest
from unittest.mock import patch, MagicMock, mock_open

from chunkydl.utils import get_output, get_name_from_url, _download_actual, convert_urls
from chunkydl.exceptions import RequestFailedException, OutputPathRequiredException
from chunkydl import DownloadConfig, DLGroup


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

    def test_handles_urls_with_query_parameters(self):
        url = "http://example.com/path/to/file.txt?query=param"
        expected = "file.txt"
        result = get_name_from_url(url)
        self.assertEqual(expected, result)

    def test_deals_with_urls_that_have_no_file_name_in_path(self):
        url = "http://example.com/path/to/"
        expected = ""
        result = get_name_from_url(url)
        self.assertEqual(expected, result)

    def test_handles_urls_with_different_schemes(self):
        urls = [
            "http://example.com/path/to/file.txt",
            "https://example.com/path/to/file.txt",
            "ftp://example.com/path/to/file.txt"
        ]
        expected = "file.txt"
        for url in urls:
            result = get_name_from_url(url)
            self.assertEqual(result, expected)


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

    def test_raises_exception_when_no_output_path_is_provided(self):
        url = "http://example.com/file"
        timeout = 10
        headers = {}
        chunk_size = 1024

        with self.assertRaises(OutputPathRequiredException):
            _download_actual(url, None, timeout, headers, chunk_size)

    def test_raises_exception_when_empty_output_path_is_provided(self):
        url = "http://example.com/file"
        timeout = 10
        headers = {}
        chunk_size = 1024

        with self.assertRaises(OutputPathRequiredException):
            _download_actual(url, '', timeout, headers, chunk_size)

    # TODO: test that additional kwargs supplied to _download_actual are used in the request header


class TestConvertUrls(unittest.TestCase):

    def test_list_of_urls_are_all_converted(self):
        output_path = '/path/to/directory/'
        config = DownloadConfig()
        urls = [
            'http://example.com/file.txt',
            'http://example_two.com/file.jpg',
            'http://example.com/file_four_hundered.mp4',
        ]

        groups = convert_urls(urls, output_path, config)
        self.assertEqual(len(urls), len(groups))
        for index, group in enumerate(groups):
            self.assertTrue(isinstance(group, DLGroup))
            self.assertEqual(urls[index], group.url)
            self.assertEqual(output_path, group.output_path)
            self.assertEqual(config, group.config)

    def test_list_of_dlgroups_are_unchanged(self):
        output_path = '/path/to/directory/'
        config = DownloadConfig()
        urls = [
            DLGroup('http://example.com/file.txt', output_path + 'one.txt', config),
            DLGroup('http://example_two.com/file.jpg', output_path + 'two.jpg', config),
            DLGroup('http://example.com/file_four_hundered.mp4', output_path + 'three.mp4', config),
        ]

        groups = convert_urls(urls, output_path, config)
        self.assertEqual(len(urls), len(groups))
        for index, group in enumerate(groups):
            self.assertEqual(urls[index], group)

    def test_mixed_list_is_handled_correctly(self):
        output_path = '/path/to/directory/'
        config = DownloadConfig()
        urls = [
            'http://example.com/file.txt',
            'http://example.com/file_four_hundered.mp4',
            DLGroup('http://example_two.com/file.jpg', output_path + 'three.jpg', config),
            DLGroup('http://example.com/filefilefile.mp4', output_path + 'four.mp4', config),
        ]

        groups = convert_urls(urls, output_path, config)
        self.assertEqual(len(urls), len(groups))
        for index, group in enumerate(groups):
            self.assertTrue(isinstance(group, DLGroup))

    def test_handles_empty_url_list(self):
        urls = []
        groups = convert_urls(urls, '/downloads', DownloadConfig())
        self.assertEqual([], groups)
