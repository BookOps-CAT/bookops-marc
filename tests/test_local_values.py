from datetime import datetime

import pytest

from bookops_marc.local_values import (
    _add_oclc_prefix,
    _delete_oclc_prefix,
    get_branch_code,
    get_shelf_audience_code,
    get_shelf_code,
    has_oclc_prefix,
    is_oclc_number,
    oclcNo_with_prefix,
    oclcNo_without_prefix,
    normalize_dewey,
    shorten_dewey,
    normalize_date,
    normalize_location_code,
    normalize_order_number,
)


@pytest.mark.parametrize(
    "arg,expectation",
    [
        ("1", "ocm00000001"),
        ("12345678", "ocm12345678"),
        ("123456789", "ocn123456789"),
        ("1234567890", "on1234567890"),
    ],
)
def test_add_oclc_prefix(arg, expectation):
    assert _add_oclc_prefix(arg) == expectation


@pytest.mark.parametrize(
    "arg,expectation", [("", ValueError), (None, TypeError), (1, TypeError)]
)
def test_add_oclc_prefix_exceptions(arg, expectation):
    with pytest.raises(expectation):
        _add_oclc_prefix(arg)


@pytest.mark.parametrize(
    "arg,expectation",
    [
        ("ocm00000001", "1"),
        ("ocn123456789", "123456789"),
        ("on1234567890", "1234567890"),
        ("(ocolc)1", "1"),
    ],
)
def test_delete_oclc_prefix(arg, expectation):
    assert _delete_oclc_prefix(arg) == expectation


@pytest.mark.parametrize(
    "arg,expectation", [("", ValueError), (None, AttributeError), (1, AttributeError)]
)
def test_delete_oclc_prefix_exceptions(arg, expectation):
    with pytest.raises(expectation):
        _delete_oclc_prefix(arg)


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
        ("foo", False),
        ("", False),
        ("123456789", False),
    ],
)
def test_has_oclc_prefix(arg, expectation):
    assert has_oclc_prefix(arg) == expectation


@pytest.mark.parametrize(
    "arg",
    [None, 1, []],
)
def test_has_oclc_prefix_exceptions(arg):
    with pytest.raises(TypeError) as exc:
        has_oclc_prefix(arg)

    assert "OCLC number must be a string." in str(exc.value)


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
    ],
)
def test_is_oclc_number(arg, expectation):
    assert is_oclc_number(arg) == expectation


@pytest.mark.parametrize(
    "arg,expectation",
    [
        ("1", "ocm00000001"),
        ("12345678", "ocm12345678"),
        ("123456789", "ocn123456789"),
        ("1234567890", "on1234567890"),
        (1, "ocm00000001"),
        (12345678, "ocm12345678"),
        (123456789, "ocn123456789"),
        (1234567890, "on1234567890"),
    ],
)
def test_oclcNo_with_prefix(arg, expectation):
    assert oclcNo_with_prefix(arg) == expectation


@pytest.mark.parametrize(
    "arg,expectation", [(None, TypeError), ("", ValueError), ([], TypeError)]
)
def test_oclcNo_with_prefix_exceptions(arg, expectation):
    with pytest.raises(expectation):
        oclcNo_with_prefix(arg)


@pytest.mark.parametrize(
    "arg,expectation",
    [
        ("ocm00000001", "1"),
        ("ocm12345678", "12345678"),
        ("ocn123456789", "123456789"),
        ("on1234567890", "1234567890"),
        (1, "1"),
        (12345678, "12345678"),
    ],
)
def test_oclcNo_without_prefix(arg, expectation):
    assert oclcNo_without_prefix(arg) == expectation


@pytest.mark.parametrize("arg", [None, []])
def test_oclcNo_without_prefix_exception(arg):
    with pytest.raises(TypeError) as exc:
        oclcNo_without_prefix(arg)
    assert "OCLC number must be a string or integer." in str(exc.value)


@pytest.mark.parametrize(
    "arg,expectation",
    [
        ("[Fic]", None),
        ("[E]", None),
        ("909", "909"),
        ("001.54", "001.54"),
        ("362.84/924043809049", "362.84924043809049"),
        ("362.84/9040", "362.84904"),
        ("j574", "574"),
        ("942.082 [B]", "942.082"),
        ("364'.971", "364.971"),
        ("C364/.971", "364.971"),
        ("505 ", "505"),
        ("900", "900"),
        ("900.100", "900.1"),
        (None, None),
    ],
)
def test_normalize_dewey(arg, expectation):
    assert normalize_dewey(arg) == expectation


@pytest.mark.parametrize(
    "arg,expectation",
    [
        ("(3)sn", "sn"),
        ("(2)btj0f", "btj0f"),
        ("41anf(5)", "41anf"),
        ("41anf", "41anf"),
        ("(3)snj0y", "snj0y"),
    ],
)
def test_normalize_location_code(arg, expectation, stub_bib):
    assert normalize_location_code(arg) == expectation


@pytest.mark.parametrize(
    "arg,expectation",
    [("41anf", "41"), ("02jje", "02"), ("snj0f", "sn"), ("fty0n", "ft")],
)
def test_get_branch_code(arg, expectation):
    assert get_branch_code(arg) == expectation


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


@pytest.mark.parametrize(
    "arg,expectation", [("41", None), ("41anf", "a"), ("snj0y", "j"), ("sn   ", None)]
)
def test_get_shelf_audience_code(arg, expectation):
    assert get_shelf_audience_code(arg) == expectation


@pytest.mark.parametrize(
    "arg,expectation",
    [
        ("41anf", "nf"),
        ("13anb", "nb"),
        ("snj0f", "0f"),
        ("tb", None),
        ("tb   ", None),
        (None, None),
    ],
)
def test_get_shelf_code(arg, expectation):
    assert get_shelf_code(arg) == expectation


def test_normalize_order_number():
    assert normalize_order_number(".o28876714") == 2887671


@pytest.mark.parametrize(
    "arg1,arg2,expectation",
    [
        ("505", 4, "505"),
        ("362.84924043809049", 4, "362.8492"),
        ("362.849040", 4, "362.849"),
        ("900", 4, "900"),
        ("512.1234", 2, "512.12"),
    ],
)
def test_shorten_dewey(arg1, arg2, expectation):
    assert shorten_dewey(class_mark=arg1, digits_after_period=arg2) == expectation
