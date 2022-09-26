from contextlib import nullcontext as does_not_rise

from pymarc import Field
import pytest

from bookops_marc.order import (
    Order,
    get_branch_code,
    get_shelf_audience_code,
    get_shelf_code,
    normalize_location_code,
    normalize_order_number,
)


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


@pytest.mark.parametrize("arg", [None, 123])
def test_order_invalid_library_arg_type(stub_960, stub_961, arg):
    with pytest.raises(TypeError) as exc:
        Order(library=arg, fixed_field=stub_960, variable_field=stub_961)

    assert "Invalid 'library' argument type. Must be a string." in str(exc.value)


def test_order_invalid_library_arg_value(stub_960, stub_961):
    with pytest.raises(ValueError) as exc:
        Order(library="foo", fixed_field=stub_960, variable_field=stub_961)

    assert "Invalid 'library' argument value. Must be 'BPL' or 'NYPL'."


def test_order_invalid_fixed_field_arg(stub_961):
    with pytest.raises(TypeError) as exc:
        Order("BPL", None, stub_961)

    assert (
        "Invalid 'fixed_field' argument. Must be pymarc.field.Field instance."
        in str(exc.value)
    )


def test_order_invalid_variable_field_arg(stub_960):
    with pytest.raises(TypeError) as exc:
        Order("BPL", stub_960, "foo")

    assert (
        "Invalid 'variable_field' argument. Must be pymarc.field.Field or None."
        in str(exc.value)
    )


def test_order_variable_field_is_none(stub_960):
    with does_not_rise():
        Order("BPL", stub_960, None)


@pytest.mark.parametrize("arg", ["BPL", "NYPL", "bpl", "nypl"])
def test_order_acceptable_library_args(stub_960, arg):
    with does_not_rise():
        Order(library=arg, fixed_field=stub_960)
