import pytest

from bookops_marc.order import OrderReader, Order


def test_OrderReader_invalid_library_arg(stub_bib):
    with pytest.raises(ValueError) as exc:
        OrderReader(library="foo", bib=stub_bib)

    assert (
        "Invalid 'library` argument passed. Only 'BPL' or 'NYPL' are permitted."
        in str(exc.value)
    )
