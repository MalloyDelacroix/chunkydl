import unittest

from chunkydl import DownloadConfig


class TestConfigHeaders(unittest.TestCase):

    def test_default_headers_are_returned_when_no_additional_are_supplied(self):
        config = DownloadConfig()
        headers = config.get_headers()
        self.assertEqual(DownloadConfig.default_headers, headers)

    def test_default_headers_with_additional_are_returned_when_only_additional_headers_are_supplied(self):
        config = DownloadConfig(additional_headers={'foo': 'bar'})
        control_headers = DownloadConfig.default_headers
        control_headers['foo'] = 'bar'

        headers = config.get_headers()
        self.assertEqual(control_headers, headers)

    def test_only_complete_headers_are_returned_when_complete_headers_are_supplied(self):
        complete_headers = {'foo': 'bar'}
        config = DownloadConfig(headers=complete_headers)

        headers = config.get_headers()
        self.assertEqual(complete_headers, headers)

    def test_kwargs_supplied_to_get_headers_are_correctly_added_to_returned_headers(self):
        kwargs = {'foo': 'bar'}
        config = DownloadConfig()
        headers = config.get_headers(**kwargs)
        control_headers = DownloadConfig.default_headers
        control_headers['foo'] = 'bar'
        self.assertEqual(control_headers, headers)

        config = DownloadConfig(additional_headers={'rackem': 'rack'})
        headers = config.get_headers(**kwargs)
        control_headers['rackem'] = 'rack'
        self.assertEqual(control_headers, headers)

        config = DownloadConfig(headers={'gaba': 'gool'})
        control_headers = {'gaba': 'gool', 'foo': 'bar'}
        headers = config.get_headers(**kwargs)
        self.assertEqual(control_headers, headers)

    def test_that_kwargs_supplied_to_get_headers_do_not_change_class_header_values(self):
        config = DownloadConfig()
        control_headers = config.get_headers()
        self.assertEqual(DownloadConfig.default_headers, control_headers)
        mod_headers = config.get_headers(foo='bar')
        headers = config.get_headers()
        self.assertEqual(control_headers, headers)

    def test_that_setting_headers_overwrites_complete_headers_and_that_the_change_persists(self):
        config = DownloadConfig()
        control_headers = config.get_headers()
        config.headers = {'foo': 'bar'}
        headers = config.get_headers()
        self.assertNotEqual(control_headers, headers)
        self.assertEqual({'foo': 'bar'}, headers)

    def test_headers_and_get_headers_return_same_value_when_no_kwargs_are_supplied(self):
        config = DownloadConfig(additional_headers={'foo': 'bar'})
        headers = config.headers
        got_headers = config.get_headers()
        self.assertEqual(headers, got_headers)
