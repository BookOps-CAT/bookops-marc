import pytest

from bookops_marc.item import Item


@pytest.mark.parametrize(
    "library, tag, indicators",
    [
        ("nypl", "949", (" ", "1")),
        ("bpl", "949", (" ", "1")),
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
        assert item.item_id == "i123456789"
        assert item.item_id_normalized == 12345678
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
        assert item.item_id_normalized is None
        assert item.copies is None
        assert item.initials is None
        assert item.internal_note is None
        assert item.item_code_1 is None
        assert item.item_code_2 is None
        assert item.item_status is None
        assert item.opac_message is None
