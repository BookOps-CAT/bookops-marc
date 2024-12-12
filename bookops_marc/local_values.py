"""
This module contains helper methods for parsing and manipulating local Sierra fields
"""

from datetime import datetime, date
from typing import Union, Optional


class OclcNumber:
    def __init__(self, value: str):
        self.value = value

    @property
    def value(self) -> str:
        return self._value

    @value.setter
    def value(self, value: Union[str, int, None]) -> None:
        if isinstance(value, str) and value.startswith("(OCoLC)"):
            self._value = value
        else:
            self._value = str(value).lower().strip()
        if not self.is_valid(self.value):
            raise ValueError("Invalid OCLC Number.")

    @property
    def has_prefix(self) -> bool:
        oclc_lower = self.value.lower()
        if (
            oclc_lower.startswith("ocm")
            or oclc_lower.startswith("ocn")
            or oclc_lower.startswith("on")
            or oclc_lower.startswith("(ocolc)")
        ):
            return True
        else:
            return False

    @property
    def with_prefix(self) -> str:
        if self.has_prefix is True and not self.value.startswith("(OCoLC)"):
            return self.value
        else:
            num = str(int(self.value.strip("(OCoLC)")))
            value_length = len(num)
            if value_length <= 8 and value_length >= 1:
                return f"ocm{str(int(num)).zfill(8)}"
            elif value_length == 9:
                return f"ocn{str(int(num))}"
            else:
                return f"on{str(int(num))}"

    @property
    def without_prefix(self) -> str:
        if not self.has_prefix:
            return self.value
        else:
            return str(int(self.value.lower().strip("()oclnm")))

    @staticmethod
    def is_valid(value: Union[str, int, None]) -> bool:
        """
        Determines if given value looks like a legitimate OCLC number.

        Args:
            value:
                identifier as `str`, `int`, or None

        Returns:
            bool
        """
        str_value = str(value).lower()
        num_value = str_value.strip("oclmn()")
        if not value:
            return False
        elif not isinstance(value, str) and not isinstance(value, int):
            return False
        elif str_value.isnumeric() is True and int(value) > 0:
            return True
        elif (
            num_value.isnumeric()
            and (str_value.startswith("ocm") and len(num_value) == 8)
            or (str_value.startswith("ocn") and len(num_value) == 9)
            or (str_value.startswith("on") and len(num_value) >= 10)
            or (str_value.startswith("(ocolc)") and len(num_value) >= 8)
        ):
            return True
        else:
            return False


def normalize_date(order_date: str) -> Optional[date]:
    """
    Returns order created date in datetime format
    """
    try:
        if len(order_date) == 8:
            return datetime.strptime(order_date[:8], "%m-%d-%y").date()
        else:
            return datetime.strptime(order_date[:10], "%m-%d-%Y").date()
    except (ValueError, TypeError):
        return None
