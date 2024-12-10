from datetime import datetime

import pytest

from bookops_marc.local_values import OclcNumber, normalize_date


@pytest.mark.parametrize(
    "value, without_pref, with_pref, has_pref",
    [
        ("ocm12345678", "12345678", "ocm12345678", True),
        ("12345678", "12345678", "ocm12345678", False),
        ("ocn123456789", "123456789", "ocn123456789", True),
        ("123456789", "123456789", "ocn123456789", False),
        ("on1234567890", "1234567890", "on1234567890", True),
        ("1234567890", "1234567890", "on1234567890", False),
        ("(OCoLC)00123456", "123456", "ocm00123456", True),
        ("(OCoLC)01234567", "1234567", "ocm01234567", True),
    ],
)
def test_OclcNumber(value, without_pref, with_pref, has_pref):
    num = OclcNumber(value)
    assert num.value == value
    assert num.has_prefix == has_pref
    assert num.with_prefix == with_pref
    assert num.without_prefix == without_pref


@pytest.mark.parametrize(
    "arg,expectation",
    [
        ("ocm00000001", True),
        ("ocn123456789", True),
        ("on1234567890", True),
        ("OCM12345678", True),
        ("OCN123456789", True),
        ("ON1234567890", True),
        ("(OCoLC)123456789", True),
        ("123456789", False),
        ("1", False),
    ],
)
def test_OclcNumber_has_prefix(arg, expectation):
    assert OclcNumber(arg).has_prefix == expectation


@pytest.mark.parametrize(
    "arg,expectation",
    [
        ("1", "ocm00000001"),
        ("12345678", "ocm12345678"),
        ("123456789", "ocn123456789"),
        ("1234567890", "on1234567890"),
    ],
)
def test_OclcNumber_with_prefix(arg, expectation):
    assert OclcNumber(arg).with_prefix == expectation


@pytest.mark.parametrize(
    "arg,expectation",
    [
        ("ocm00000001", "1"),
        ("ocn123456789", "123456789"),
        ("on1234567890", "1234567890"),
    ],
)
def test_OclcNumber_without_prefix(arg, expectation):
    assert OclcNumber(arg).without_prefix == expectation


def test_OclcNumber_setter():
    num = OclcNumber("ocm12345678")
    assert num.has_prefix is True
    assert num.with_prefix == "ocm12345678"
    assert num.without_prefix == "12345678"
    assert num.value == "ocm12345678"
    num.value = "12345678901"
    assert num.has_prefix is False
    assert num.with_prefix == "on12345678901"
    assert num.without_prefix == "12345678901"
    assert num.value != "ocm12345678"


@pytest.mark.parametrize(
    "value",
    [
        "foo",
        "foo12345678",
        "bar123456789",
        "0",
        "(ocolc)1",
        "ocm1",
        "ocm111111111",
        "ocn1",
        "ocn11111111111",
        "on1",
        None,
        0,
        "",
        [],
        {"oclcNumber": "ocm00000001"},
    ],
)
def test_OclcNumber_invalid(value):
    with pytest.raises(ValueError) as exc:
        num = OclcNumber(value)
        assert num.value == value
        assert hasattr(num, "has_prefix") is False
        assert hasattr(num, "with_prefix") is False
        assert hasattr(num, "without_prefix") is False
    assert str(exc.value) == "Invalid OCLC Number."


@pytest.mark.parametrize(
    "arg,expectation",
    [
        ("ocm00000001", True),
        ("ocm12345678", True),
        ("ocn123456789", True),
        ("on1234567890", True),
        ("0", False),
        (1, True),
        (1234567890, True),
        (None, False),
        ("", False),
        (0, False),
        ([], False),
        ({"oclcNumber": "ocm00000001"}, False),
        ("foo", False),
        ("foo12345678", False),
        ("bar123456789", False),
        ("0", False),
        ("(ocolc)1", False),
        ("ocm1", False),
        ("ocm111111111", False),
        ("ocn1", False),
        ("ocn11111111111", False),
        ("on1", False),
    ],
)
def test_OclcNumber_is_valid(arg, expectation):
    assert OclcNumber.is_valid(arg) == expectation


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
