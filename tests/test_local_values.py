from datetime import datetime

import pytest

from bookops_marc.local_values import normalize_date


@pytest.mark.parametrize(
    "arg,expectation",
    [
        ("01-30-21", datetime(2021, 1, 30)),
        ("08-02-2021 16:19", datetime(2021, 8, 2)),
        ("  -  -  ", None),
    ],
)
def test_normalize_date(arg, expectation):
    if expectation is not None:
        assert normalize_date(arg) == expectation.date()
    else:
        assert normalize_date(arg) is None
