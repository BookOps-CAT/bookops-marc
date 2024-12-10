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


def get_branch_code(location_code: str) -> str:
    """
    Returns branch code from normalized location code
    """
    branch = location_code[:2]
    return branch


def get_shelf_audience_code(location_code: str) -> Optional[str]:
    """
    Parses audience code from given normalized location_code
    """
    try:
        audn = location_code[2].strip()
        if audn:
            return audn
        else:
            return None

    except IndexError:
        return None


def get_shelf_code(location_code: str) -> Optional[str]:
    """
    Parses shelf code from given normalized location_code
    """
    try:
        shelf = location_code[3:5].strip()
        if shelf:
            return shelf
        else:
            return None
    except (TypeError, IndexError):
        return None


def normalize_date(order_date: str) -> Optional[date]:
    """
    Returns order created date in datetime format
    """
    try:
        if len(order_date) == 8:
            return datetime.strptime(order_date[:8], "%m-%d-%y").date()
        else:
            return datetime.strptime(order_date[:10], "%m-%d-%Y").date()
    except ValueError:
        return None


def normalize_dewey(class_mark: str) -> Optional[str]:
    """
    Normalizes Dewey classification to be used in call numbers

    Args:
        class_mark:                  Dewey classification

    Returns:
        normalized class_mark
    """
    if isinstance(class_mark, str):
        class_mark = (
            class_mark.replace("/", "")
            .replace("j", "")
            .replace("C", "")
            .replace("[B]", "")
            .replace("'", "")
            .strip()
        )
        try:
            float(class_mark)
        except ValueError:
            return None
        else:
            while len(class_mark) > 4 and class_mark[-1] == "0":
                class_mark = class_mark[:-1]
            return class_mark
    else:
        return None


def normalize_location_code(code: str) -> str:
    """
    Removes any quantity designation from location code value
    """
    try:
        s = code.index("(")
        e = code.index(")")
        return f"{code[:s]}{code[e + 1:]}"
    except ValueError:
        return code


def normalize_order_number(order_number: str) -> int:
    """
    Normalizes Sierra order number
    """
    return int(order_number[2:-1])


def shorten_dewey(class_mark: str, digits_after_period: int = 4) -> str:
    """
    Shortens Dewey classification number to maximum 4 digits after period.
    BPL materials: default 4 digits - 505.4167
    NYPl adult/young adult: default 4 digits
    NYPL juvenile materials:    2 digits - 618.54

    Args:
        class_mark:                 Dewey classification
        digits_after_period:        number of allowed digits after period

    Returns:
        shortened class_mark

    """
    class_mark = class_mark[: 4 + digits_after_period]
    while len(class_mark) > 3 and class_mark[-1] in ".0":
        class_mark = class_mark[:-1]
    return class_mark
