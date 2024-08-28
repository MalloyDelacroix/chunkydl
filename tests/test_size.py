import unittest

from chunkydl import Size


class TestSize(unittest.TestCase):

    def test_size_works_for_bytes_single_str_value(self):
        value = Size('1b')
        self.assertEqual(1, value)

    def test_size_works_for_kb_single_str_value(self):
        value = Size('1kb')
        self.assertEqual(1024, value)

    def test_size_works_for_mb_single_str_value(self):
        value = Size('1mb')
        self.assertEqual(1024 ** 2, value)

    def test_size_works_for_gb_single_str_value(self):
        value = Size('1gb')
        self.assertEqual(1024 ** 3, value)

    def test_size_works_for_tb_single_str_value(self):
        value = Size('1tb')
        self.assertEqual(1024 ** 4, value)

    def test_size_uses_bytes_when_no_size_unit_is_provided_single_str_value(self):
        value = Size('487')
        self.assertEqual(487, value)

    def test_size_handles_decimals_correctly(self):
        value = Size('1.236gb')
        self.assertEqual(int(1.236 * 1024 ** 3), value)

    def test_that_spaces_are_ignored(self):
        value = Size('256                                    mb')
        self.assertEqual(256 * 1024 ** 2, value)

    def test_that_capitalization_is_ignored(self):
        value = Size('12GB')
        self.assertEqual(12 * 1024 ** 3, value)

    def test_size_uses_bytes_when_unit_is_provided(self):
        value = Size(256, 'b')
        self.assertEqual(256, value)

    def test_size_uses_kb_when_unit_is_provided(self):
        value = Size(34, 'kb')
        self.assertEqual(34 * 1024, value)

    def test_size_uses_mb_when_unit_is_provided(self):
        value = Size(34, 'mb')
        self.assertEqual(34 * 1024 ** 2, value)

    def test_size_uses_gb_when_unit_is_provided(self):
        value = Size(34, 'gb')
        self.assertEqual(34 * 1024 ** 3, value)

    def test_size_uses_tb_when_unit_is_provided(self):
        value = Size(34, 'tb')
        self.assertEqual(34 * 1024 ** 4, value)

    def test_size_uses_bytes_when_no_unit_is_provided_int_value(self):
        value = Size(256)
        self.assertEqual(256, value)

    def test_unit_specified_with_value_is_preferred_if_unit_is_also_provided(self):
        value = Size('256gb', 'mb')
        self.assertEqual(256 * 1024 ** 3, value)

    def test_defaults_to_bytes_when_invalid_format_is_provided(self):
        value = Size('23 pj')
        self.assertEqual(23, value)

        value = Size('23 bg')
        self.assertEqual(23, value)

        value = Size('23 elves')
        self.assertEqual(23, value)

        value = Size('345 238')
        self.assertEqual(345, value)

        value = Size('345 8df sd0f9u sldkfj')
        self.assertEqual(345, value)
