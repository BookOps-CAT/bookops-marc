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
