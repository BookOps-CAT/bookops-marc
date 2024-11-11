import pytest

from pymarc import Field, Record, Subfield, Indicators

from bookops_marc import Bib


@pytest.fixture
def stub_pymarc_record():
    record = Record()
    record.leader = "02866pam  2200517 i 4500"
    record.add_field(Field(tag="008", data="190306s2017    ht a   j      000 1 hat d"))
    record.add_field(
        Field(
            tag="100",
            indicators=Indicators("1", " "),
            subfields=[
                Subfield(code="a", value="Adams, John,"),
                Subfield(code="e", value="author."),
            ],
        )
    )
    record.add_field(
        Field(
            tag="245",
            indicators=Indicators("1", "4"),
            subfields=[
                Subfield(code="a", value="The foo /"),
                Subfield(code="c", value="by John Adams."),
            ],
        )
    )
    record.add_field(
        Field(
            tag="264",
            indicators=Indicators(" ", "1"),
            subfields=[
                Subfield(code="a", value="Bar :"),
                Subfield(code="b", value="New York,"),
                Subfield(code="c", value="2021"),
            ],
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
            indicators=Indicators("1", " "),
            subfields=[
                Subfield(code="a", value="Adams, John,"),
                Subfield(code="e", value="author."),
            ],
        )
    )
    bib.add_field(
        Field(
            tag="245",
            indicators=Indicators("1", "4"),
            subfields=[
                Subfield(code="a", value="The foo /"),
                Subfield(code="c", value="by John Adams."),
            ],
        )
    )
    bib.add_field(
        Field(
            tag="264",
            indicators=Indicators(" ", "1"),
            subfields=[
                Subfield(code="a", value="Bar :"),
                Subfield(code="b", value="New York,"),
                Subfield(code="c", value="2021"),
            ],
        )
    )
    return bib


@pytest.fixture
def mock_960():
    # fmt: off
    return Field(tag="960", indicators=Indicators(" ", " "), subfields=[
        Subfield(code="a", value="l"),  # acq type
        Subfield(code="b", value="-"),  # ?
        Subfield(code="c", value="j"),  # order code 1 (selector)
        Subfield(code="d", value="c"),  # order code 2 (NYPL library; BPL audn)
        Subfield(code="e", value="d"),  # order code 3 (NYPL source; BPL not used)
        Subfield(code="f", value="a"),  # order code 4 (NYPL audn; BPL Opac display)
        Subfield(code="g", value="b"),  # form
        Subfield(code="h", value="-"),  # ?
        Subfield(code="i", value="l"),  # order type
        Subfield(code="j", value="-"),  # ?
        Subfield(code="m", value="o"),  # status
        Subfield(code="n", value="-"),  # ?
        Subfield(code="p", value="  -  -  "),  # ?
        Subfield(code="q", value="08-02-21"),  # order date
        Subfield(code="r", value="  -  -  "),  # ?
        Subfield(code="s", value="{{dollar}}13.20"),  # price
        Subfield(code="t", value="(3)snj0y"),  # location
        Subfield(code="t", value="agj0y"),
        Subfield(code="t", value="muj0y"),
        Subfield(code="t", value="inj0y"),
        Subfield(code="o", value="13"),  # copies
        Subfield(code="u", value="lease"),  # fund
        Subfield(code="v", value="btlea"),  # vendor
        Subfield(code="w", value="eng"),  # lang
        Subfield(code="x", value="xxu"),  # country
        Subfield(code="y", value="1"),  # volumes
        Subfield(code="z", value=".o10000010")  # order#
    ])
    # fmt: on
