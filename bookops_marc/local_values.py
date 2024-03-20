"""
This module contains helper methods for parsing and manipulating local Sierra fields
"""

from datetime import datetime, date
from typing import Union, Optional


def _add_oclc_prefix(value: str) -> str:
    """
    Prefixes given OCLC identifier expressed as digits with
    'ocm', 'ocn", and 'on' depending on the length of the identifier.
    Given OCLC identifier must be already normalized.

    Args:
        value:          normalized OCLC identifier expressed as a `str`

    Returns:
        oclcNo_prefixed
    """
    value_length = len(value)

    if value_length <= 8 and value_length >= 1:
        return f"ocm{str(int(value)).zfill(8)}"
    elif value_length == 9:
        return f"ocn{str(int(value))}"
    elif value_length > 9:
        return f"on{str(int(value))}"
    else:
        return str(int(value))


def _delete_oclc_prefix(value: str) -> str:
    """
    Removes any prefixes from OCLC identifer.

    Args:
        value:          normalized OCLC identifer expressed as `str`

    Returns:
        OCLC identifier without any prefixes as a `str`
    """
    if value.startswith("ocm") or value.startswith("ocn"):
        return str(int(value[3:]))
    elif value.startswith("on"):
        return str(int(value[2:]))
    elif value.startswith("(ocolc)"):
        return str(int(value[7:]))
    else:
        return str(int(value))


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


def has_oclc_prefix(oclcNo: str) -> bool:
    """
    Determines if the given OCLC number has a prefix.

    Args:
        oclcNo:         OCLC number expressed as a str:
    """
    if isinstance(oclcNo, str):
        if (
            oclcNo.lower().startswith("ocm")
            or oclcNo.lower().startswith("ocn")
            or oclcNo.lower().startswith("on")
        ):
            return True
        elif oclcNo.lower().startswith("(ocolc)"):
            return True
        else:
            return False
    else:
        raise TypeError("OCLC number must be a string.")


def is_oclc_number(value: Union[str, int]) -> bool:
    """
    Determines if given value looks like a legitimate OCLC number.

    Args:
        value:          identifier as `str` or `int`

    Returns:
        bool
    """
    if isinstance(value, str):
        if has_oclc_prefix(value):
            return True
        else:
            try:
                if int(value) > 0:
                    return True
                else:
                    return False
            except ValueError:
                return False
    elif isinstance(value, int):
        if int(value) > 0:
            return True
        else:
            return False
    else:
        return False


def oclcNo_with_prefix(oclcNo: Union[str, int]) -> str:
    """
    Adds OCLC prefix to given OCLC number without one

    Args:
        oclcNo:         OCLC number expressed as `str` or `int`

    Returns:
        OCLC identifier with a correct prefix as a `str`
    """
    if isinstance(oclcNo, str):
        oclcNo_norm = oclcNo.lower().strip()
        if has_oclc_prefix(oclcNo_norm):
            return oclcNo_norm
        else:
            return _add_oclc_prefix(oclcNo_norm)

    elif isinstance(oclcNo, int):
        oclcNo_norm = str(oclcNo).lower().strip()
        return _add_oclc_prefix(oclcNo_norm)

    else:
        raise TypeError("OCLC number must be a string or integer.")


def oclcNo_without_prefix(oclcNo: Union[str, int]) -> str:
    """
    Removes OCLC prefix from given OCLC identifier.

    Args:
        oclcNo:         OCLC identifier expressed as `str` or `int`

    Returns:
        OCLC identifier witouth any prefixes as a `str`
    """
    if isinstance(oclcNo, str):
        oclcNo_norm = oclcNo.lower().strip()
        if has_oclc_prefix(oclcNo_norm):
            return _delete_oclc_prefix(oclcNo_norm)
        else:
            return oclcNo_norm
    elif isinstance(oclcNo, int):
        oclcNo_norm = str(oclcNo).lower().strip()
        return oclcNo_norm
    else:
        raise TypeError("OCLC number must be a string or integer.")


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
