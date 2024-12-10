import datetime
import pytest
from bookops_marc.models import Item, Order


def test_Item(stub_945):
    item = Item(field=stub_945)
    assert item.agency == "043"
    assert item.barcode == "33433123456789"
    assert item.call_no == "ReCAP 25-000001"
    assert item.call_tag == "8528"
    assert item.item_id == ".i123456789"
    assert item.item_message == "foo"
    assert item.location == "rc2ma"
    assert item.opac_message == "bar"
    assert item.price == "$5.00"
    assert item.type == "55"
    assert item.vendor_code == "LEILA"
    assert item.volume == "1"


def test_Item_missing_subfield(stub_945):
    stub_945.delete_subfield("u")
    item = Item(field=stub_945)
    assert item.agency == "043"
    assert item.barcode == "33433123456789"
    assert item.call_no == "ReCAP 25-000001"
    assert item.call_tag == "8528"
    assert item.item_id == ".i123456789"
    assert item.item_message is None
    assert item.location == "rc2ma"
    assert item.opac_message == "bar"
    assert item.price == "$5.00"
    assert item.type == "55"
    assert item.vendor_code == "LEILA"
    assert item.volume == "1"


def test_Item_too_many_subfields(stub_945):
    stub_945.add_subfield(code="i", value="33433111111111")
    with pytest.raises(ValueError) as exc:
        Item(stub_945)
    assert str(exc.value) == "Subfield i is non-repeatable."


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
    [("41", []), ("41anf", ["a"]), ("snj0y", ["j"]), ("sn   ", []), (None, [])],
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
        ("41anf", ["nf"]),
        ("13anb", ["nb"]),
        ("snj0f", ["0f"]),
        ("tb", []),
        ("tb   ", []),
        (None, []),
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
        (".o28876714", 2887671),
        (".o12345678", 1234567),
        (".o10000000", 1000000),
    ],
)
def test_Order_oid(arg, expectation, stub_960, stub_961):
    stub_960.delete_subfield("z")
    stub_960.add_subfield(code="z", value=arg)
    order = Order(field=stub_960, following_field=stub_961)
    assert order.oid == expectation


def test_Order_missing_order_number(stub_960, stub_961):
    stub_960.delete_subfield("z")
    stub_960.add_subfield(code="z", value=None)
    with pytest.raises(ValueError) as exc:
        Order(field=stub_960, following_field=stub_961)
    assert str(exc.value) == "Order field must contain an order number (960$z)"
