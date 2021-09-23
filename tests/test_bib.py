"""
Tests bib.py module
"""
from copy import deepcopy
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


@pytest.mark.parametrize(
    "arg,expectation",
    [
        ("01-30-21", datetime(2021, 1, 30)),
        ("08-02-2021 16:19", datetime(2021, 8, 2)),
        ("  -  -  ", None),
    ],
)
def test_normalize_date(arg, expectation):
    if expectation is not None:
        assert normalize_date(arg) == expectation.date()
    else:
        assert normalize_date(arg) is None


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


def test_sierra_bib_id_missing_tag(stub_marc):
    assert stub_marc.sierra_bib_id() is None


def test_sierra_bib_id_missing_subfield(stub_marc):
    stub_marc.add_field(
        Field(
            tag="907",
            indicators=[" ", " "],
            subfields=["b", "08-17-21$c08-17-2021 7:50"],
        )
    )
    assert stub_marc.sierra_bib_id() is None


def test_sierra_bib_id(stub_marc):
    stub_marc.add_field(
        Field(
            tag="907",
            indicators=[" ", " "],
            subfields=["a", ".b225444884", "b", "08-17-21$c08-17-2021 7:50"],
        )
    )
    assert stub_marc.sierra_bib_id() == "b225444884"


def test_sierra_bib_id_normalized(stub_marc):
    stub_marc.add_field(
        Field(
            tag="907",
            indicators=[" ", " "],
            subfields=["a", ".b225444884", "b", "08-17-21$c08-17-2021 7:50"],
        )
    )
    assert stub_marc.sierra_bib_id_normalized() == "22544488"


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


@pytest.mark.parametrize("arg", ["08-02-2021 16:19", "08-02-21"])
def test_created_date(stub_marc, arg):
    stub_marc.add_field(
        Field(
            tag="907",
            subfields=["a", ".b225375965", "b", "08-17-21", "c", arg],
        )
    )
    assert stub_marc.created_date() == datetime(2021, 8, 2).date()


def test_cataloging_date(stub_marc):
    stub_marc.add_field(
        Field(
            tag="907",
            subfields=["a", ".b225375965", "b", "08-17-21", "c", "08-02-21"],
        )
    )
    assert stub_marc.cataloging_date() == datetime(2021, 8, 17).date()


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


def test_dewey_shortened(stub_marc):
    stub_marc.add_field(
        Field(tag="082", indicators=[" ", " "], subfields=["a", "900.092"])
    )
    stub_marc.add_field(
        Field(tag="082", indicators=["0", "4"], subfields=["a", "910.092"])
    )
    stub_marc.add_field(
        Field(tag="082", indicators=["0", "0"], subfields=["a", "909./09208"])
    )
    assert stub_marc.dewey_shortened() == "909.092"


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


def test_lccn_missing_010(stub_marc):
    assert stub_marc.lccn() is None


def test_lccn_missing_sub_a(stub_marc):
    stub_marc.add_field(Field(tag="010", indicators=[" ", " "], subfields=["z", "foo"]))
    assert stub_marc.lccn() is None


@pytest.mark.parametrize(
    "arg,expectation",
    [
        ("   85153773 ", "85153773"),
        ("nuc76039265 ", "nuc76039265"),
        ("  2001627090", "2001627090"),
    ],
)
def test_lccn(arg, expectation, stub_marc):
    stub_marc.add_field(
        Field(tag="010", indicators=[" ", " "], subfields=["a", arg, "b", "foo"])
    )
    assert stub_marc.lccn() == expectation


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


@pytest.mark.parametrize("arg", [1, "foo"])
def test_orders_exceptions(arg, stub_marc, mock_960):
    msg = "Invalid 'sort' argument was passed."
    stub_marc.add_field(mock_960)
    with pytest.raises(BookopsMarcError) as exc:
        stub_marc.orders(sort=arg)
    assert msg in str(exc)


def test_orders_single(stub_marc, mock_960):
    stub_marc.add_field(mock_960)
    stub_marc.add_field(
        Field(
            tag="961",
            indicators=[" ", " "],
            subfields=["h", "e,bio", "l", "1643137123"],
        )
    )
    orders = stub_marc.orders()
    assert len(orders) == 1
    o = orders[0]
    assert o.oid == 1000001
    assert o.audn == ["j", "j", "j", "j"]
    assert o.status == "o"
    assert o.branches == ["sn", "ag", "mu", "in"]
    assert o.copies == 13
    assert o.created == datetime(2021, 8, 2).date()
    assert o.shelves == ["0y", "0y", "0y", "0y"]
    assert o.form == "b"
    assert o.lang == "eng"
    assert o.venNotes == "e,bio"


def test_orders_reverse_sort(stub_marc, mock_960):
    stub_marc.add_field(mock_960)
    stub_marc.add_field(
        Field(
            tag="961",
            indicators=[" ", " "],
            subfields=["h", "e,bio", "l", "1643137123"],
        )
    )
    # add second 960 without 961
    second_960 = deepcopy(mock_960)
    second_960.delete_subfield("z")
    second_960.add_subfield("z", ".o10000020")
    stub_marc.add_field(second_960)
    orders = stub_marc.orders(sort="descending")

    assert len(orders) == 2
    assert orders[0].oid == 1000002
    assert orders[0].venNotes is None
    assert orders[1].oid == 1000001
    assert orders[1].venNotes == "e,bio"


def test_overdrive_number_missing_037(stub_marc):
    assert stub_marc.overdrive_number() is None


def test_overdrive_number_missing_sub_a(stub_marc):
    stub_marc.add_field(Field(tag="037", indicators=[" ", " "], subfields=["z", "foo"]))
    assert stub_marc.overdrive_number() is None


@pytest.mark.parametrize(
    "arg,expectation",
    [
        (
            "EA72608D-6B04-446E-9AAC-4131D2E529C6",
            "EA72608D-6B04-446E-9AAC-4131D2E529C6",
        ),
        (
            " EA72608D-6B04-446E-9AAC-4131D2E529C6 ",
            "EA72608D-6B04-446E-9AAC-4131D2E529C6",
        ),
    ],
)
def test_overdrive_number(arg, expectation, stub_marc):
    stub_marc.add_field(
        Field(
            tag="037",
            indicators=[" ", " "],
            subfields=["a", arg, "b", "OverDrive, Inc."],
        )
    )
    assert stub_marc.overdrive_number() == expectation


def test_subjects_lc(stub_marc):
    stub_marc.add_field(
        Field(tag="650", indicators=[" ", "7"], subfields=["a", "Foo", "2", "bar"])
    )
    stub_marc.add_field(
        Field(
            tag="600",
            indicators=["1", "0"],
            subfields=["a", "Doe, John", "x", "Childhood."],
        )
    )
    stub_marc.add_field(
        Field(tag="650", indicators=[" ", "4"], subfields=["a", "Foo", "2", "bar"])
    )
    stub_marc.add_field(
        Field(tag="651", indicators=[" ", "0"], subfields=["a", "Spam."])
    )
    lc_subjects = stub_marc.subjects_lc()
    assert len(lc_subjects) == 2
    assert lc_subjects[0].subfields == ["a", "Doe, John", "x", "Childhood."]
    assert lc_subjects[1].subfields == ["a", "Spam."]


def test_upc_number_missing_024(stub_marc):
    assert stub_marc.upc_number() is None


def test_upc_number_missing_sub_a(stub_marc):
    stub_marc.add_field(Field(tag="024", indicators=["1", " "], subfields=["z", "foo"]))
    assert stub_marc.upc_number() is None


def test_upc_number_other_number(stub_marc):
    stub_marc.add_field(
        Field(
            tag="024", indicators=["2", " "], subfields=["a", "M011234564", "z", "foo"]
        )
    )
    assert stub_marc.upc_number() is None


@pytest.mark.parametrize(
    "arg,expectation",
    [
        (
            "7822183031",
            "7822183031",
        ),
        (
            " 7822183031 ",
            "7822183031",
        ),
    ],
)
def test_upc_number(arg, expectation, stub_marc):
    stub_marc.add_field(
        Field(
            tag="024",
            indicators=["1", " "],
            subfields=["a", arg, "b", "foo"],
        )
    )
    assert stub_marc.upc_number() == expectation
