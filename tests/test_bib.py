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
