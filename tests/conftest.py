import pytest

from pymarc import Field, Record

from bookops_marc import Bib


@pytest.fixture
def stub_pymarc_record():
    record = Record()
    record.leader = "02866pam  2200517 i 4500"
    record.add_field(Field(tag="008", data="190306s2017    ht a   j      000 1 hat d"))
    record.add_field(
        Field(
            tag="100",
            indicators=["1", " "],
            subfields=["a", "Adams, John,", "e", "author."],
        )
    )
    record.add_field(
        Field(
            tag="245",
            indicators=["1", "4"],
            subfields=["a", "The foo /", "c", "by John Adams."],
        )
    )
    record.add_field(
        Field(
            tag="264",
            indicators=[" ", "1"],
            subfields=["a", "Bar :", "b", "New York,", "c", "2021"],
        )
    )
    return record


@pytest.fixture
def stub_bib():
    bib = Bib()
    bib.leader = "02866pam  2200517 i 4500"
    bib.add_field(Field(tag="008", data="190306s2017    ht a   j      000 1 hat d"))
    bib.add_field(
        Field(
            tag="100",
            indicators=["1", " "],
            subfields=["a", "Adams, John,", "e", "author."],
        )
    )
    bib.add_field(
        Field(
            tag="245",
            indicators=["1", "4"],
            subfields=["a", "The foo /", "c", "by John Adams."],
        )
    )
    bib.add_field(
        Field(
            tag="264",
            indicators=[" ", "1"],
            subfields=["a", "Bar :", "b", "New York,", "c", "2021"],
        )
    )
    return bib


@pytest.fixture
def mock_960():
    # fmt: off
    return Field(tag="960", indicators=[" ", " "], subfields=[
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
        "z", ".o10000010"  # order#
    ])
    # fmt: on
