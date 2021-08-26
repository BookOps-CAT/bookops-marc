"""
Tests bib.py module
"""
from datetime import datetime

import pytest

from pymarc import Field

from bookops_marc.bib import (
    get_branch_code,
    get_shelf_audience_code,
    get_shelf_code,
    normalize_dewey,
    shorten_dewey,
    normalize_date,
    normalize_location_code,
    normalize_order_number,
)
from bookops_marc.errors import BookopsMarcError


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
        (None, None),
    ],
)
def test_normalize_dewey(arg, expectation):
    assert normalize_dewey(arg) == expectation


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
def test_normalize_location_code(arg, expectation, stub_marc):
    assert normalize_location_code(arg) == expectation


@pytest.mark.parametrize(
    "arg,expectation",
    [("41anf", "41"), ("02jje", "02"), ("snj0f", "sn"), ("fty0n", "ft")],
)
def test_get_branch_code(arg, expectation):
    assert get_branch_code(arg) == expectation


def test_normalize_date():
    assert normalize_date("01-07-21") == datetime(2021, 7, 1)


@pytest.mark.parametrize(
    "arg,expectation", [("41", None), ("41anf", "a"), ("snj0y", "j")]
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


def test_sierra_bib_no_missing_tag(stub_marc):
    assert stub_marc.sierra_bib_no() is None


def test_sierra_bib_no_missing_subfield(stub_marc):
    stub_marc.add_field(
        Field(
            tag="907",
            indicators=[" ", " "],
            subfields=["b", "08-17-21$c08-17-2021 7:50"],
        )
    )
    assert stub_marc.sierra_bib_no() is None


def test_sierra_bib_no(stub_marc):
    stub_marc.add_field(
        Field(
            tag="907",
            indicators=[" ", " "],
            subfields=["a", ".b225444884", "b", "08-17-21$c08-17-2021 7:50"],
        )
    )
    assert stub_marc.sierra_bib_no() == "b225444884"


def test_sierra_bib_no_normalized(stub_marc):
    stub_marc.add_field(
        Field(
            tag="907",
            indicators=[" ", " "],
            subfields=["a", ".b225444884", "b", "08-17-21$c08-17-2021 7:50"],
        )
    )
    assert stub_marc.sierra_bib_no_normalized() == "22544488"


@pytest.mark.parametrize(
    "arg1,arg2,arg3,expectation",
    [
        ("bpl", "099", ["a", "FIC", "a", "FOO"], "FIC FOO"),
        ("bpl", "091", ["a", "FIC", "a", "FOO"], None),
        ("nypl", "091", ["a", "FIC", "c", "FOO"], "FIC FOO"),
        ("nypl", "099", ["a", "FIC", "c", "FOO"], None),
        ("", "091", ["a", "FIC", "c", "FOO"], None),
    ],
)
def test_branch_call_no(stub_marc, arg1, arg2, arg3, expectation):
    stub_marc.library = arg1
    stub_marc.add_field(Field(tag=arg2, indicators=[" ", " "], subfields=arg3))
    assert stub_marc.branch_call_no() == expectation


def test_audience_missing_008(stub_marc):
    stub_marc.remove_fields("008")
    assert stub_marc.audience() is None


@pytest.mark.parametrize(
    "arg1,arg2,expectation",
    [
        ("a", "a", "j"),
        ("a", "m", "j"),
        ("c", "a", "j"),
        ("c", "m", "j"),
        ("d", "a", "j"),
        ("d", "m", "j"),
        ("g", "a", "j"),
        ("g", "m", "j"),
        ("i", "a", "j"),
        ("i", "m", "j"),
        ("j", "a", "j"),
        ("k", "a", "j"),
        ("k", "m", "j"),
        ("m", "a", "j"),
        ("m", "m", "j"),
        ("t", "a", "j"),
        ("t", "m", "j"),
        ("e", "a", None),  # map
        ("a", "s", None),  # serial
    ],
)
def test_audience(stub_marc, arg1, arg2, expectation):
    s = list(stub_marc.leader)
    s[6] = arg1
    s[7] = arg2
    stub_marc.leader = "".join(s)
    assert stub_marc.audience() == expectation


def test_record_type(stub_marc):
    assert stub_marc.record_type() == "a"


def test_physical_description_no_300_tag(stub_marc):
    assert stub_marc.physical_description() is None


@pytest.mark.parametrize(
    "tags,expectation",
    [
        (["100", "245"], "100"),
        (["110", "245"], "110"),
        (["111", "245"], "111"),
        (["245"], "245"),
    ],
)
def test_main_entry(stub_marc, tags, expectation):
    stub_marc.remove_fields("100", "245")
    for t in tags:
        stub_marc.add_field(Field(tag=t, subfields=["a", "foo"]))
    main_entry = stub_marc.main_entry()
    assert type(main_entry) == Field
    assert main_entry.tag == expectation


def test_dewey_no_082(stub_marc):
    assert stub_marc.dewey() is None


def test_dewey_lc_selected(stub_marc):
    stub_marc.add_field(
        Field(tag="082", indicators=[" ", " "], subfields=["a", "900./092"])
    )
    stub_marc.add_field(
        Field(tag="082", indicators=["0", "4"], subfields=["a", "909.092"])
    )
    stub_marc.add_field(
        Field(tag="082", indicators=["0", "0"], subfields=["a", "909.12"])
    )
    assert stub_marc.dewey() == "909.12"


def test_dewey_other_agency_selected(stub_marc):
    stub_marc.add_field(Field(tag="082", indicators=["1", "0"], subfields=["a", "900"]))
    stub_marc.add_field(
        Field(tag="082", indicators=["0", "4"], subfields=["a", "909./092"])
    )
    assert stub_marc.dewey() == "909.092"


def test_dewey_normalized(stub_marc):
    stub_marc.add_field(
        Field(tag="082", indicators=[" ", " "], subfields=["a", "900.092"])
    )
    stub_marc.add_field(
        Field(tag="082", indicators=["0", "4"], subfields=["a", "910.092"])
    )
    stub_marc.add_field(
        Field(tag="082", indicators=["0", "0"], subfields=["a", "909./09208"])
    )
    assert stub_marc.dewey_normalized() == "909.092"


def test_languages_none_008(stub_marc):
    stub_marc.remove_fields("008")
    assert stub_marc.languages() == []


def test_languages_only_008_present(stub_marc):
    assert stub_marc.languages() == ["hat"]


def test_languages_multiple(stub_marc):
    stub_marc.add_field(
        Field(tag="041", subfields=["a", "eng", "a", "spa", "b", "chi", "h", "rus"])
    )
    assert stub_marc.languages() == ["hat", "eng", "spa"]


def test_form_of_item_not_present(stub_marc):
    stub_marc.leader = "#" * 6 + "x" + "#" * 18
    stub_marc["008"].data = "#" * 23 + "f" + "#" * 10
    assert stub_marc.form_of_item() is None


@pytest.mark.parametrize("arg", ["a", "c", "d", "i", "j", "m", "o", "p", "t"])
def test_form_of_item_in_pos_23(arg, stub_marc):
    stub_marc.leader = "#" * 6 + arg + "#" * 18
    stub_marc["008"].data = "#" * 23 + "f" + "#" * 10
    assert stub_marc.form_of_item() == "f"


@pytest.mark.parametrize("arg", ["e", "f", "g", "k"])
def test_form_of_item_in_pos_29(arg, stub_marc):
    stub_marc.leader = "#" * 6 + arg + "#" * 18
    stub_marc["008"].data = "#" * 29 + "o" + "#" * 14
    assert stub_marc.form_of_item() == "o"


@pytest.mark.parametrize(
    "arg,expectation",
    [
        (
            None,
            "Must specify 'library' argument. Order field mapping varies between both systems.",
        ),
        (5, "The 'library' argument  must be a string."),
        (
            "queens",
            "The 'library' argument have only two permissable values: 'nypl' and 'bpl'.",
        ),
    ],
)
def test_orders_exceptions(arg, expectation, stub_marc):
    with pytest.raises(BookopsMarcError) as exc:
        stub_marc.orders(library=arg)
    assert expectation in str(exc)


def test_orders(stub_marc):
    # fmt: off
    stub_marc.add_field(Field(tag="960", indicators=[" ", " "], subfields=[
        "a", "l",  # acq type
        "b", "-",  # ?
        "c", "j",  # order code 1 (selector)
        "d", "c",  # order code 2 (NYPL library; BPL audn)
        "e", "d",  # order code 3 (NYPL source; BPL not used)
        "f", "a",  # order code 4 (NYPL audn; BPL Opac display)
        "g", "b",  # form
        "h", "-",  # ?
        "i", "l",  # order type
        "j", "-",  # ?
        "m", "o",  # status
        "n", "-",  # ?
        "p", "  -  -  ",  # ?
        "q", "08-02-21",  # order date
        "r", "  -  -  ",  # ?
        "s", "{{dollar}}13.20",  # price
        "t", "(3)snj0y",  # location
        "t", "agj0y",
        "t", "muj0y",
        "t", "inj0y",
        "o", "13",  # copies
        "u", "lease",  # fund
        "v", "btlea",  # vendor
        "w", "eng",  # lang
        "x", "xxu",  # country
        "y", "1",  # volumes
        "z", ".o28876714"  # order#
    ]))
    # fmt: on
    orders = stub_marc.orders(library="nypl")
    assert len(orders) == 1
    o = orders[0]
    assert o.oid == 2887671
    assert o.audn == "j"
    assert o.status == "o"
    assert o.branches == ["sn", "ag", "mu", "in"]
    assert o.copies == 13
    assert o.created == datetime(2021, 2, 8)
    assert o.shelves == ["0y", "0y", "0y", "0y"]
