"""
Tests bib.py module
"""
import pytest

from pymarc import Field


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
