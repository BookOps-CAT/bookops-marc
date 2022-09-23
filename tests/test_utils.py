from datetime import datetime

from bookops_marc.utils import sierra_str2date

import pytest


@pytest.mark.parametrize(
    "arg,expectation",
    [
        ("01-30-22", datetime(2022, 1, 30).date()),
        ("01-30-2022", datetime(2022, 1, 30).date()),
        ("01-30-2022 12:12", datetime(2022, 1, 30).date()),
        ("foo", None),
        ("2022-01-30", None),
        ("  -  -  ", None),
    ],
)
def test_sierra_str2date(arg, expectation):
    assert sierra_str2date(arg) == expectation
