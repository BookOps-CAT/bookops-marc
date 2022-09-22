from contextlib import nullcontext as does_not_rise

from pymarc import Field
import pytest

from bookops_marc.order import get_orders, Order


# def test_get_orders_invalid_library_arg(stub_bib):
#     with pytest.raises(ValueError) as exc:
#         get_orders(library="foo", bib=stub_bib)

#     assert (
#         "Invalid 'library' argument passed. Only 'BPL' or 'NYPL' are permitted."
#         in str(exc.value)
#     )


# def test_get_orders_invalid_bib_arg():
#     with pytest.raises(ValueError) as exc:
#         get_orders("BPL", None)

#     assert (
#         "Invalid argument 'bib' was passed. Must be bookops_marc.bib.Bib or pymarc.record.Record instance."
#         in str(exc.value)
#     )


# @pytest.mark.parametrize("arg", ["BPL", "NYPL", "bpl", "nypl"])
# def test_get_orders_acceptable_library_args(stub_bib, arg):
#     with does_not_rise():
#         get_orders(library=arg, bib=stub_bib)


# def test_get_orders_no_data(stub_bib):
#     stub_bib.remove_fields("960", "961")
#     assert get_orders("BPL", stub_bib) == []


# def test_get_orders(stub_bib):
# 	stub_bib.add_fields(Field(tag="960", indicators=[" ", " "], subfields=["a", "foo"]))
