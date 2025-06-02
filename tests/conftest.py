import pytest
from pymarc import Field, Indicators, Record, Subfield

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
    bib.add_field(
        Field(
            tag="949",
            indicators=Indicators(" ", " "),
            subfields=[Subfield(code="a", value="*b2=a;")],
        )
    )
    return bib


@pytest.fixture
def mock_960():
    return Field(
        tag="960",
        indicators=Indicators(" ", " "),
        subfields=[
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
            Subfield(code="z", value=".o10000010"),  # order#
        ],
    )


@pytest.fixture
def stub_960():
    return Field(
        tag="960",
        indicators=Indicators(" ", " "),
        subfields=[
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
            Subfield(code="o", value="13"),  # copies
            Subfield(code="p", value="  -  -  "),  # ?
            Subfield(code="q", value="08-02-21"),  # order date
            Subfield(code="r", value="  -  -  "),  # ?
            Subfield(code="s", value="{{dollar}}13.20"),  # price
            Subfield(code="t", value="agj0y"),
            Subfield(code="u", value="lease"),  # fund
            Subfield(code="v", value="btlea"),  # vendor
            Subfield(code="w", value="eng"),  # lang
            Subfield(code="x", value="xxu"),  # country
            Subfield(code="y", value="1"),  # volumes
            Subfield(code="z", value=".o10000010"),  # order#
        ],
    )


@pytest.fixture
def stub_961():
    return Field(
        tag="961",
        indicators=Indicators(" ", " "),
        subfields=[
            Subfield(code="h", value="foo"),  # vendor notes
        ],
    )


@pytest.fixture
def stub_949_command_line():
    return Field(
        tag="949",
        indicators=Indicators(" ", " "),
        subfields=[
            Subfield(code="a", value="ReCAP 25-000001"),
            Subfield(code="h", value="043"),
            Subfield(code="i", value="33433123456789"),
            Subfield(code="z", value="8528"),
            Subfield(code="t", value="55"),
            Subfield(code="u", value="foo"),
            Subfield(code="m", value="bar"),
            Subfield(code="l", value="rc2ma"),
            Subfield(code="p", value="$5.00"),
            Subfield(code="v", value="LEILA"),
            Subfield(code="c", value="1"),
            Subfield(code="y", value=".i123456789"),
        ],
    )


@pytest.fixture
def stub_item(tag, indicators):
    return Field(
        tag=tag,
        indicators=indicators,
        subfields=[
            Subfield(code="a", value="ReCAP 25-000001"),
            Subfield(code="g", value="1"),
            Subfield(code="h", value="043"),
            Subfield(code="i", value="33433123456789"),
            Subfield(code="z", value="8528"),
            Subfield(code="t", value="55"),
            Subfield(code="u", value="-"),
            Subfield(code="m", value="bar"),
            Subfield(code="n", value="baz"),
            Subfield(code="l", value="rc2ma"),
            Subfield(code="o", value="-"),
            Subfield(code="p", value="$5.00"),
            Subfield(code="q", value="-"),
            Subfield(code="r", value="-"),
            Subfield(code="s", value="b"),
            Subfield(code="v", value="LEILA"),
            Subfield(code="c", value="1"),
            Subfield(code="y", value=".i123456789"),
        ],
    )


@pytest.fixture
def stub_field():
    return Field(
        tag="999",
        indicators=Indicators(" ", " "),
        subfields=[Subfield(code="a", value="foo")],
    )
