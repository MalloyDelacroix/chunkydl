import logging
import os
import unittest
from unittest.mock import patch, Mock, mock_open

from chunkydl.multi_part_downloader import MultiPartDownloader
from chunkydl import DownloadConfig


class TestRun(unittest.TestCase):

    def test_calculate_chunks(self):
        """
        Tests that the correct number of chunks are calculated based on the file size and the size threshold.
        """
        config = Mock()
        config.size_threshold = 100
        config.multi_part_thread_count = 4
        url = 'http://example.com/file'
        output_path = '/path/to/directory'
        file_size = 450
        downloader = MultiPartDownloader(url, output_path, file_size=file_size, config=config)
        mock_executor = Mock()
        downloader.executor = mock_executor
        downloader.get_output_path = Mock()
        downloader.download_part = Mock()
        mock_join_file = Mock()
        downloader.join_file = mock_join_file

        downloader.run()

        self.assertEqual(downloader.part_count, 5)
        mock_executor.shutdown.assert_called_once()
        mock_join_file.assert_called_once()


    def test_exact_divisible_file_size(self):
        """
        Tests that the correct number of chunks are calculated when the file size is exactly divisible by the threshold.
        """
        config = Mock()
        config.size_threshold = 100
        config.multi_part_thread_count = 4
        url = 'http://example.com/file'
        output_path = '/path/to/directory'
        file_size = 300
        downloader = MultiPartDownloader(url, output_path, file_size=file_size, config=config)
        mock_executor = Mock()
        downloader.executor = mock_executor
        downloader.get_output_path = Mock()
        downloader.download_part = Mock()
        mock_join_file = Mock()
        downloader.join_file = mock_join_file

        downloader.run()

        self.assertEqual(downloader.part_count, 3)
        mock_executor.shutdown.assert_called_once()
        mock_join_file.assert_called_once()

    def test_smaller_file_size_than_threshold(self):
        """
        Tests that the correct number of chunks are calculated when the file size is smaller than the threshold.
        """
        config = Mock()
        config.size_threshold = 100
        config.multi_part_thread_count = 4
        url = 'http://example.com/file'
        output_path = '/path/to/directory'
        file_size = 50
        downloader = MultiPartDownloader(url, output_path, file_size=file_size, config=config)
        mock_executor = Mock()
        downloader.executor = mock_executor
        downloader.get_output_path = Mock()
        downloader.download_part = Mock()
        mock_join_file = Mock()
        downloader.join_file = mock_join_file

        downloader.run()

        self.assertEqual(downloader.part_count, 1)
        mock_executor.shutdown.assert_called_once()
        mock_join_file.assert_called_once()


class TestJoinFile(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        logging.disable(logging.CRITICAL)

    @patch('chunkydl.multi_part_downloader.MultiPartDownloader.remove_temp_path')
    @patch('chunkydl.multi_part_downloader.ThreadPoolExecutor')
    @patch('builtins.open', new_callable=mock_open)
    def test_temp_dir_is_removed_on_completion(self, mock_file, mock_executor, mock_remove_path):
        downloader = MultiPartDownloader(
            url='http://example.com/file.mp4', output_path='/path/to/directory', file_size=400, config=DownloadConfig()
        )
        downloader.join_file()
        mock_remove_path.assert_called_once()

    @patch('builtins.open', new_callable=mock_open)
    @patch('chunkydl.multi_part_downloader.MultiPartDownloader.remove_temp_path')
    @patch('chunkydl.multi_part_downloader.ThreadPoolExecutor')
    @patch('chunkydl.multi_part_downloader.MultiPartDownloader.write_parts_to_file', side_effect=FileNotFoundError)
    def test_temp_dir_is_removed_on_failure_when_specified(self, mock_write, mock_executor, mock_remove_path,
                                                           mock_file):
        config = DownloadConfig(clean_up_on_fail=True)
        downloader = MultiPartDownloader(
            url='http://example.com/file.mp4', output_path='/path/to/directory', file_size=400, config=config
        )
        downloader.join_file()
        mock_remove_path.assert_called_once()

    @patch('builtins.open', new_callable=mock_open)
    @patch('chunkydl.multi_part_downloader.MultiPartDownloader.remove_temp_path')
    @patch('chunkydl.multi_part_downloader.ThreadPoolExecutor')
    @patch('chunkydl.multi_part_downloader.MultiPartDownloader.write_parts_to_file', side_effect=FileNotFoundError)
    def test_temp_dir_is_not_removed_on_failure_when_specified(self, mock_write, mock_executor, mock_remove_path,
                                                           mock_file):
        config = DownloadConfig(clean_up_on_fail=False)
        downloader = MultiPartDownloader(
            url='http://example.com/file.mp4', output_path='/path/to/directory', file_size=400, config=config
        )
        downloader.join_file()
        mock_remove_path.assert_not_called()

class TestGetOutputPath(unittest.TestCase):

    @patch('chunkydl.multi_part_downloader.ThreadPoolExecutor')
    @patch('tempfile.mkdtemp')
    def test_does_not_create_temp_dir_when_class_variable_exists(self, mock_mkdtemp, mock_executor):
        """
        When the MultiPartDownloader class' temp_path variable has already been set, it should be used instead of
        creating a new temp directory when get output path is called.
        """
        config = Mock()
        url = 'http://example.com/file'
        output_path = '/path/to/directory/test_name.txt'
        file_size = 450
        downloader = MultiPartDownloader(url, output_path, file_size=file_size, config=config)
        temp_path = '/path/to/temp_directory'
        downloader.temp_path = temp_path

        expected_path = os.path.join(temp_path, 'test_name.txt.part-4')
        path = downloader.get_output_path(4)
        self.assertEqual(expected_path, path)
        mock_mkdtemp.assert_not_called()

    @patch('chunkydl.multi_part_downloader.ThreadPoolExecutor')
    @patch('tempfile.mkdtemp')
    def test_does_create_temp_dir_when_no_class_variable_exists(self, mock_mkdtemp, mock_executor):
        """
        If the class' temp_path variable does not already exist, a new temporary directory should be created and
        temp_path should be set to its path.
        """
        config = Mock()
        url = 'http://example.com/file'
        output_path = '/path/to/directory/test_name.txt'
        file_size = 450
        temp_path = '/path/to/temp_directory'
        mock_mkdtemp.return_value = temp_path
        downloader = MultiPartDownloader(url, output_path, file_size=file_size, config=config)

        expected_path = os.path.join(temp_path, 'test_name.txt.part-4')
        path = downloader.get_output_path(4)
        self.assertEqual(expected_path, path)
        self.assertEqual(temp_path, downloader.temp_path)
        mock_mkdtemp.assert_called_with(dir='/path/to/directory')

    @patch('chunkydl.multi_part_downloader.ThreadPoolExecutor')
    @patch('tempfile.mkdtemp')
    def test_handles_output_path_as_directory(self, mock_mkdtemp, mock_executor):
        """
        When no output name has been derived, the path returned should include the file name taken from the url
        basename.
        """
        output_path = os.path.join('path', 'to', 'directory')
        temp_path = os.path.join(output_path, 'temp_dir')
        mock_mkdtemp.return_value = temp_path
        downloader = MultiPartDownloader(
            url='http://example.com/file.mp4', output_path=output_path, file_size=400, config=DownloadConfig()
        )
        downloader.output_name = None

        output_path = downloader.get_output_path(4)

        expected_output = os.path.join(temp_path, 'file.mp4.part-4')
        self.assertEqual(expected_output, output_path)

    @patch('tempfile.mkdtemp', side_effect=OSError('Failed to create temp directory'))
    def test_handles_temporary_directory_creation_failure(self, mock_mkdtemp):
        downloader = MultiPartDownloader(
            url='http://example.com/file.mp4', output_path='/path/to/directory', file_size=400, config=DownloadConfig()
        )
        with self.assertRaises(OSError):
            downloader.get_output_path(4)

