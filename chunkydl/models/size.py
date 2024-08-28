import re
from typing import Union, Optional


class Size(int):

    """
    A custom class for representing sizes with units. Inherits from int.

    Private attributes:
        _value_multiplier (dict): A dictionary that maps units to multipliers.
    """

    _value_multiplier = {
        'b': 1,
        'kb': 1024,
        'mb': 1024 ** 2,
        'gb': 1024 ** 3,
        'tb': 1024 ** 4,
    }

    def __new__(cls, size: Union[str, int], unit: Optional[str] = None) -> int:
        """
        Creates a new instance of Size with the given size and unit, converting them to bytes.

        Parameters:
            size (Union[str, int]): The size value to be converted to bytes.  May be an int if the unit parameter is
                supplied or you wish for the size to be in bytes.  May be a string value containing the size as a number
                followed by the unit that the size uses (ie: 3.4MB).
            unit (Optional[str]): The unit of the size value. May be b, kb, mb, gb, or tb.  Capitalization does not
                matter. Defaults to None.

        Returns:
            int: The size value converted to bytes.
        """
        size_in_bytes = cls._parse_size(size, unit)
        return super().__new__(cls, size_in_bytes)

    @classmethod
    def _parse_size(cls, size: Union[str, int], unit: Optional[str]) -> int:
        """
        Parses the given size value and unit to convert the size value to bytes.

        Parameters:
            size (Union[str, int]): The size value to be converted to bytes.
            unit (Optional[str]): The unit of the size value. Defaults to None.

        Returns:
            int: The size value converted to bytes.

        Raises:
            ValueError: If the size format is invalid.
        """
        if unit is not None and isinstance(size, int):
            return int(float(size) * cls._value_multiplier[unit.lower()])
        size = str(size)
        match = re.match(r'(\d+(\.\d+)?)\s*(b|kb|mb|gb|tb)?', size.lower().strip())
        size_value = float(match.group(1))
        unit = match.group(3) if match.group(3) else 'b'
        return int(size_value * cls._value_multiplier[unit])

    def __repr__(self):
        return f'{int(self)} bytes'
