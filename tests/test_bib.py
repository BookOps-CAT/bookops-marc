"""
Tests bib.py module
"""
import pytest

from pymarc import Field

from bookops_marc.bib import normalize_dewey, shorten_dewey


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
