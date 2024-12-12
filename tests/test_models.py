import datetime
import pytest
from bookops_marc.models import Order


def test_Order(mock_960, stub_961):
    order = Order(field=mock_960, following_field=stub_961)
    assert order.audn == ["j", "j", "j", "j"]
    assert order.branches == ["sn", "ag", "mu", "in"]
    assert order.copies == 13
    assert order.created == datetime.date(2021, 8, 2)
    assert order.form == "b"
    assert order.lang == "eng"
    assert order.locs == ["snj0y", "agj0y", "muj0y", "inj0y"]
    assert order.oid == 1000001
    assert order.shelves == ["0y", "0y", "0y", "0y"]
    assert order.status == "o"
    assert order.venNotes == "foo"


def test_Order_other_following_field(mock_960, stub_field):
    order = Order(field=mock_960, following_field=stub_field)
    assert stub_field.tag != "961"
    assert order.audn == ["j", "j", "j", "j"]
    assert order.branches == ["sn", "ag", "mu", "in"]
    assert order.copies == 13
    assert order.created == datetime.date(2021, 8, 2)
    assert order.form == "b"
    assert order.lang == "eng"
    assert order.locs == ["snj0y", "agj0y", "muj0y", "inj0y"]
    assert order.oid == 1000001
    assert order.shelves == ["0y", "0y", "0y", "0y"]
    assert order.status == "o"
    assert order.venNotes is None


@pytest.mark.parametrize(
    "arg,expectation",
    [
        ("41", []),
        ("41anf", ["a"]),
        ("snj0y", ["j"]),
        ("sn   ", []),
        (None, []),
        (" ", []),
        ("      ", []),
    ],
)
def test_Order_audn(arg, expectation, stub_960, stub_961):
    stub_960.delete_subfield("t")
    stub_960.add_subfield(code="t", value=arg)
    order = Order(field=stub_960, following_field=stub_961)
    assert order.audn == expectation


def test_Order_audn_no_location(stub_960, stub_961):
    stub_960.delete_subfield("t")
    order = Order(field=stub_960, following_field=stub_961)
    assert order.audn == []


@pytest.mark.parametrize(
    "arg,expectation",
    [
        ("41anf", ["41"]),
        ("02jje", ["02"]),
        ("snj0f", ["sn"]),
        ("fty0n", ["ft"]),
        ("0n", []),
        (None, []),
        (" ", []),
        ("", []),
    ],
)
def test_Order_branches(arg, expectation, stub_960, stub_961):
    stub_960.delete_subfield("t")
    stub_960.add_subfield(code="t", value=arg)
    order = Order(field=stub_960, following_field=stub_961)
    assert order.branches == expectation


def test_Order_branches_no_location(stub_960, stub_961):
    stub_960.delete_subfield("t")
    order = Order(field=stub_960, following_field=stub_961)
    assert order.branches == []


@pytest.mark.parametrize(
    "arg,expectation",
    [
        ("1", 1),
        ("02", 2),
        (2, 2),
        ("fty0n", None),
        ("0n", None),
        (None, None),
        (" ", None),
        ("      ", None),
        ("three", None),
    ],
)
def test_Order_copies(arg, expectation, stub_960, stub_961):
    stub_960.delete_subfield("o")
    stub_960.add_subfield(code="o", value=arg)
    order = Order(field=stub_960, following_field=stub_961)
    assert order.copies == expectation


def test_Order_copies_no_subfield(stub_960, stub_961):
    stub_960.delete_subfield("o")
    order = Order(field=stub_960, following_field=stub_961)
    assert order.copies is None


@pytest.mark.parametrize(
    "arg,expectation",
    [
        ("01-01-24", datetime.date(2024, 1, 1)),
        ("02-02-02", datetime.date(2002, 2, 2)),
        ("02-02-2022", datetime.date(2022, 2, 2)),
        ("foo", None),
        ("", None),
        (None, None),
    ],
)
def test_Order_created(arg, expectation, stub_960, stub_961):
    stub_960.delete_subfield("q")
    stub_960.add_subfield(code="q", value=arg)
    order = Order(field=stub_960, following_field=stub_961)
    assert order.created == expectation


def test_Order_created_no_subfield(stub_960, stub_961):
    stub_960.delete_subfield("q")
    order = Order(field=stub_960, following_field=stub_961)
    assert order.created is None


@pytest.mark.parametrize(
    "arg,expectation",
    [
        ("b", "b"),
        ("a", "a"),
        ("m", "m"),
        ("p", "p"),
        ("foo", None),
        ("", None),
        ("book", None),
        ([], None),
        (None, None),
        (
            (
                "a",
                "b",
            ),
            None,
        ),
    ],
)
def test_Order_form(arg, expectation, stub_960, stub_961):
    stub_960.delete_subfield("g")
    stub_960.add_subfield(code="g", value=arg)
    order = Order(field=stub_960, following_field=stub_961)
    assert order.form == expectation


def test_Order_form_no_subfield(stub_960, stub_961):
    stub_960.delete_subfield("g")
    order = Order(field=stub_960, following_field=stub_961)
    assert order.form is None


@pytest.mark.parametrize(
    "arg,expectation",
    [
        ("eng", "eng"),
        ("pol", "pol"),
        ("cze", "cze"),
        ("spa", "spa"),
        ("Spanish", None),
        (1, None),
        ("", None),
        ([], None),
        (None, None),
        (
            (
                "spa",
                "fre",
            ),
            None,
        ),
    ],
)
def test_Order_lang(arg, expectation, stub_960, stub_961):
    stub_960.delete_subfield("w")
    stub_960.add_subfield(code="w", value=arg)
    order = Order(field=stub_960, following_field=stub_961)
    assert order.lang == expectation


def test_Order_lang_no_subfield(stub_960, stub_961):
    stub_960.delete_subfield("w")
    order = Order(field=stub_960, following_field=stub_961)
    assert order.lang is None


@pytest.mark.parametrize(
    "arg,expectation",
    [
        ("(3)sn", ["sn"]),
        ("(2)btj0f", ["btj0f"]),
        ("41anf(5)", ["41anf"]),
        ("41anf", ["41anf"]),
        ("(3)snj0y", ["snj0y"]),
        (None, []),
    ],
)
def test_Order_locs(arg, expectation, stub_960, stub_961):
    stub_960.delete_subfield("t")
    stub_960.add_subfield(code="t", value=arg)
    order = Order(field=stub_960, following_field=stub_961)
    assert order.locs == expectation


def test_Order_locs_no_location(stub_960, stub_961):
    stub_960.delete_subfield("t")
    order = Order(field=stub_960, following_field=stub_961)
    assert order.locs == []


@pytest.mark.parametrize(
    "arg,expectation",
    [
        (".o28876714", 2887671),
        (".o12345678", 1234567),
        (".o10000000", 1000000),
        (None, None),
    ],
)
def test_Order_oid(arg, expectation, stub_960, stub_961):
    stub_960.delete_subfield("z")
    stub_960.add_subfield(code="z", value=arg)
    order = Order(field=stub_960, following_field=stub_961)
    assert order.oid == expectation


def test_Order_oid_no_subfield(stub_960, stub_961):
    stub_960.delete_subfield("z")
    order = Order(field=stub_960, following_field=stub_961)
    assert order.oid is None


@pytest.mark.parametrize(
    "arg,expectation",
    [
        ("41anf", ["nf"]),
        ("13anb", ["nb"]),
        ("snj0f", ["0f"]),
        ("tb", []),
        ("tb   ", []),
        (None, []),
        (" ", []),
        ("      ", []),
    ],
)
def test_Order_shelves(arg, expectation, stub_960, stub_961):
    stub_960.delete_subfield("t")
    stub_960.add_subfield(code="t", value=arg)
    order = Order(field=stub_960, following_field=stub_961)
    assert order.shelves == expectation


def test_Order_shelves_no_location(stub_960, stub_961):
    stub_960.delete_subfield("t")
    order = Order(field=stub_960, following_field=stub_961)
    assert order.shelves == []


@pytest.mark.parametrize(
    "arg,expectation",
    [
        ("2", "2"),
        ("a", "a"),
        ("o", "o"),
        ("z", "z"),
        ("foo", None),
        ("", None),
        ([], None),
        (None, None),
        (
            (
                "a",
                "b",
            ),
            None,
        ),
    ],
)
def test_Order_status(arg, expectation, stub_960, stub_961):
    stub_960.delete_subfield("m")
    stub_960.add_subfield(code="m", value=arg)
    order = Order(field=stub_960, following_field=stub_961)
    assert order.status == expectation


def test_Order_status_no_subfield(stub_960, stub_961):
    stub_960.delete_subfield("m")
    order = Order(field=stub_960, following_field=stub_961)
    assert order.status is None


@pytest.mark.parametrize(
    "arg,expectation",
    [
        ("foo", "foo"),
        ("bar", "bar"),
        ("baz", "baz"),
        ("", ""),
        (None, None),
    ],
)
def test_Order_venNotes(arg, expectation, stub_960, stub_961):
    stub_961.delete_subfield("h")
    stub_961.add_subfield(code="h", value=arg)
    order = Order(field=stub_960, following_field=stub_961)
    assert order.venNotes == expectation


def test_Order_venNotes_no_subfield(stub_960, stub_961):
    stub_961.delete_subfield("h")
    order = Order(field=stub_960, following_field=stub_961)
    assert order.venNotes is None


def test_Order_venNotes_no_961(stub_960):
    order = Order(field=stub_960, following_field=None)
    assert order.venNotes is None
