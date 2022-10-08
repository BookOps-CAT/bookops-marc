from contextlib import nullcontext as does_not_rise
from datetime import datetime

from pymarc import Field
import pytest

from bookops_marc.order import (
    Order,
    get_branch_code,
    get_shelf_audience_code,
    get_shelf_code,
    normalize_location_code,
    normalize_order_number,
    normalize_vendor_note,
)


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


def test_normalize_order_number():
    assert normalize_order_number(".o28876714") == 2887671


@pytest.mark.parametrize(
    "arg,expectation",
    [
        ("foo", "foo"),
        ("FOO", "foo"),
        ("foo,bar", "foo,bar"),
        ("Foo,Bar", "foo,bar"),
        ("foo , bar", "foo,bar"),
        (" foo  ,  bar  ", "foo,bar"),
        (",foo", "foo"),
        ("foo,", "foo"),
        (" , ", None),
        ("foo;bar", "foo,bar"),
        (" Foo ;  Bar ", "foo,bar"),
        ("; Foo", "foo"),
        ("", None),
        (None, None),
        ("e", None),
        ("e,bio", "bio"),
        ("e,m", "m"),
        ("t,s", "t,s"),
        ("n,bio", "bio"),
        ("n, w", "w"),
        ("N,BIO", "bio"),
        ("bio, n", "bio"),
        ("ref,lit;fic", "lit,fic"),
        ("lit;non", "lit,non"),
    ],
)
def test_normalize_vendor_note(arg, expectation):
    assert normalize_vendor_note(arg) == expectation


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


def test_order_get_blanket_po(stub_960, stub_961):
    order = Order(library="nypl", fixed_field=stub_960, variable_field=stub_961)
    assert order._get_blanket_po() == "blanketPO ($p)"


@pytest.mark.parametrize("arg,expectation", [("j", "j"), ("-", None)])
def test_order_get_code1(stub_960, arg, expectation):
    stub_960["c"] = arg
    order = Order(library="nypl", fixed_field=stub_960)
    assert order._get_code1() == expectation


@pytest.mark.parametrize("arg,expectation", [("c", "c"), ("-", None)])
def test_order_get_code2(stub_960, arg, expectation):
    stub_960["d"] = arg
    order = Order(library="nypl", fixed_field=stub_960)
    assert order._get_code2() == expectation


@pytest.mark.parametrize("arg,expectation", [("d", "d"), ("-", None)])
def test_order_get_code3(stub_960, arg, expectation):
    stub_960["e"] = arg
    order = Order(library="nypl", fixed_field=stub_960)
    assert order._get_code3() == expectation


@pytest.mark.parametrize("arg,expectation", [("a", "a"), ("-", None)])
def test_order_get_code4(stub_960, arg, expectation):
    stub_960["f"] = arg
    order = Order(library="nypl", fixed_field=stub_960)
    assert order._get_code4() == expectation


@pytest.mark.parametrize("arg,expectation", [("150", 150), ("-", None), (None, None)])
def test_order_get_copies(stub_960, arg, expectation):
    stub_960["o"] = arg
    order = Order(library="nypl", fixed_field=stub_960)
    assert order._get_copies() == expectation


def test_order_get_country(stub_960):
    order = Order(library="nypl", fixed_field=stub_960)
    assert order._get_country() == "xxu"


def test_order_get_created_date(stub_960):
    order = Order(library="nypl", fixed_field=stub_960)
    order_date = datetime(2021, 2, 8).date()
    assert order._get_created_date() == order_date


def test_order_get_first_fixed_field(stub_960):
    stub_960.add_subfield(code="l", value=" foo ")
    stub_960.add_subfield(code="l", value=" bar ")

    order = Order(library="nypl", fixed_field=stub_960)
    assert order._get_first_fixed_field("l") == "foo"


def test_order_get_first_fixed_field_missing(stub_960):
    order = Order(library="nypl", fixed_field=stub_960)
    assert order._get_first_fixed_field("l") is None


def test_order_get_first_varialbe_field(stub_960, stub_961):
    stub_961.add_subfield(code="x", value=" foo ")
    stub_961.add_subfield(code="x", value=" bar ")

    order = Order(library="nypl", fixed_field=stub_960, variable_field=stub_961)
    assert order._get_first_variable_field("x") == "foo"


def test_order_get_first_variable_field_missing(stub_960, stub_961):
    order = Order(library="nypl", fixed_field=stub_960, variable_field=stub_961)
    assert order._get_first_variable_field("x") is None


@pytest.mark.parametrize("arg,expectation", [("b", "b"), ("-", None)])
def test_order_get_format(stub_960, arg, expectation):
    stub_960["g"] = arg
    order = Order(library="nypl", fixed_field=stub_960)
    assert order._get_format() == expectation


def test_order_get_funds(stub_960):
    order = Order(library="nypl", fixed_field=stub_960)
    assert order._get_funds() == tuple(["lease"])


def test_order_get_internal_note(stub_960, stub_961):
    order = Order(library="nypl", fixed_field=stub_960, variable_field=stub_961)
    assert order._get_internal_note() == "internal-note ($i)"


def test_order_get_isbn(stub_960, stub_961):
    order = Order(library="nypl", fixed_field=stub_960, variable_field=stub_961)
    assert order._get_isbn() == "ISBN ($b)"


@pytest.mark.parametrize("arg,expectation", [("eng", "eng"), ("   ", None)])
def test_order_get_language(stub_960, arg, expectation):
    stub_960["w"] = arg
    order = Order(library="nypl", fixed_field=stub_960)
    assert order._get_language_code() == expectation


def test_order_get_locations(stub_960):
    order = Order(library="nypl", fixed_field=stub_960)
    assert order._get_locations() == tuple(["sn", "ag", "mu", "in"])


@pytest.mark.parametrize("arg,expectation", [("l", "l"), ("-", None)])
def test_order_get_order_type(stub_960, arg, expectation):
    stub_960["i"] = arg
    order = Order(library="nypl", fixed_field=stub_960)
    assert order._get_order_type() == expectation


@pytest.mark.parametrize(
    "arg,expectation",
    [
        ("{{dollar}}13.20", 13.2),
        ("{{dollar}}0.0", 0.0),
        ("{{foo}}0", 0.0),
        ("9.99", 9.99),
        ("foo", None),
        ("{{dollar}}foo", None),
    ],
)
def test_order_get_price(stub_960, arg, expectation):
    stub_960["s"] = arg
    order = Order(library="nypl", fixed_field=stub_960)
    assert order._get_price() == expectation


def test_order_get_shelf_audience_codes(stub_960):
    order = Order(library="nypl", fixed_field=stub_960)
    assert order._get_shelf_audience_codes() == tuple(["j", "j", "j", "j"])


def test_order_get_shelves(stub_960):
    order = Order(library="nypl", fixed_field=stub_960)
    assert order._get_shelves() == tuple(["0y", "0y", "0y", "0y"])


def test_order_get_status(stub_960):
    order = Order(library="nypl", fixed_field=stub_960)
    assert order._get_status() == "o"


def test_order_get_vendor_code(stub_960):
    order = Order(library="nypl", fixed_field=stub_960)
    assert order._get_vendor_code() == "btlea"


def test_order_get_ventor_title_number(stub_960, stub_961):
    order = Order(library="nypl", fixed_field=stub_960, variable_field=stub_961)
    assert order._get_vendor_title_number() == "vendor-title-no ($f)"


def test_order_unique_funds(stub_960):
    stub_960.add_subfield(code="u", value="foo")
    stub_960.add_subfield(code="u", value="foo")

    assert len(stub_960.get_subfields("u")) == 3
    order = Order(library="nypl", fixed_field=stub_960)
    assert order.unique_funds() == set(["lease", "foo"])


def test_order_unique_locations(stub_960):
    stub_960.add_subfield(code="t", value="(2)snj0y")

    assert len(stub_960.get_subfields("t")) == 5
    order = Order(library="nypl", fixed_field=stub_960)
    assert order.unique_locations() == set(["sn", "ag", "mu", "in"])


def test_order_unique_shelf_audn_codes(stub_960):
    order = Order(library="nypl", fixed_field=stub_960)
    assert order.unique_shelf_audn_codes() == set(["j"])


def test_order_unique_shelves(stub_960):
    order = Order(library="nypl", fixed_field=stub_960)
    assert order.unique_shelves() == set(["0y"])


def test_order_get_vendor_note(stub_960, stub_961):
    order = Order(library="nypl", fixed_field=stub_960, variable_field=stub_961)

    assert order._get_vendor_note() == "vendor-note ($v)"
