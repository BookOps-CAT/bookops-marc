import datetime

import pytest

from bookops_marc.models import Item, OclcNumber, Order


@pytest.mark.parametrize(
    "library, tag, indicators",
    [
        ("nypl", "949", (" ", "1")),
        ("nypl", "945", (" ", " ")),
        ("bpl", "945", (" ", " ")),
        ("bpl", "960", (" ", " ")),
    ],
)
class TestItem:
    def test_Item(self, stub_item, library, tag, indicators):
        item = Item(field=stub_item)
        assert item.call_no == "ReCAP 25-000001"
        assert item.item_agency == "043"
        assert item.barcode == "33433123456789"
        assert item.item_type == "55"
        assert item.item_message == "-"
        assert item.message == "bar"
        assert item.location == "rc2ma"
        assert item.price == "$5.00"
        assert item.volume == "1"
        assert item.item_id == 12345678
        assert item.copies == "1"
        assert item.initials == "LEILA"
        assert item.internal_note == "baz"
        assert item.item_code_1 == "-"
        assert item.item_code_2 == "-"
        assert item.item_status == "b"
        assert item.opac_message == "-"

    def test_Item_empty(self, stub_item, library, tag, indicators):
        stub_item.subfields = []
        item = Item(field=stub_item)
        assert item.call_no is None
        assert item.item_agency is None
        assert item.barcode is None
        assert item.item_type is None
        assert item.item_message is None
        assert item.message is None
        assert item.location is None
        assert item.price is None
        assert item.volume is None
        assert item.item_id is None
        assert item.copies is None
        assert item.initials is None
        assert item.internal_note is None
        assert item.item_code_1 is None
        assert item.item_code_2 is None
        assert item.item_status is None
        assert item.opac_message is None


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
        ("(OCoLC)1", "1", "ocm00000001", True),
        ("(ocolc)1", "1", "ocm00000001", True),
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
        ("(OCoLC)00000001)", "1"),
        ("(OCoLC)1)", "1"),
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
        ("(ocolc)1", True),
        ("ocm1", False),
        ("ocm111111111", False),
        ("ocn1", False),
        ("ocn11111111111", False),
        ("on1", False),
    ],
)
def test_OclcNumber_is_valid(arg, expectation):
    assert OclcNumber.is_valid(arg) == expectation


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
        ("41", ["41"]),
        ("02jje", ["02"]),
        ("snj0f", ["sn"]),
        ("fty0n", ["ft"]),
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
