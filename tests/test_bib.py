"""
Tests bib.py module
"""
from copy import deepcopy
from datetime import datetime

import pytest

from pymarc import Field, Subfield

from bookops_marc.bib import (
    Bib,
    get_branch_code,
    get_shelf_audience_code,
    get_shelf_code,
    normalize_dewey,
    shorten_dewey,
    normalize_date,
    normalize_location_code,
    normalize_order_number,
    pymarc_record_to_local_bib,
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
        ("900", "900"),
        ("900.100", "900.1"),
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
def test_normalize_location_code(arg, expectation, stub_bib):
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


def test_sierra_bib_format_missing_tag(stub_bib):
    assert stub_bib.sierra_bib_format() is None


def test_sierra_bib_format_missing_subfield(stub_bib):
    stub_bib.add_field(Field(tag="998", subfields=[Subfield(code="a", value="foo")]))
    assert stub_bib.sierra_bib_format() is None


def test_sierra_bib_format(stub_bib):
    stub_bib.add_field(
        Field(
            tag="998", subfields=[Subfield(code="a", value="foo"), Subfield("d", "x  ")]
        )
    )
    assert stub_bib.sierra_bib_format() == "x"


def test_sierra_bib_id_missing_tag(stub_bib):
    assert stub_bib.sierra_bib_id() is None


def test_sierra_bib_id(stub_bib):
    stub_bib.add_field(
        Field(
            tag="907",
            indicators=[" ", " "],
            subfields=[
                Subfield(code="a", value=".b225444884"),
                Subfield(code="b", value="08-17-21$c08-17-2021 7:50"),
            ],
        )
    )
    assert stub_bib.sierra_bib_id() == "b225444884"


@pytest.mark.parametrize(
    "field,expectation",
    [
        pytest.param(
            Field(
                tag="907",
                indicators=[" ", " "],
                subfields=[Subfield(code="b", value="spam")],
            ),
            True,
            id="Spam",
        ),
        pytest.param(
            Field(
                tag="907",
                indicators=[" ", " "],
                subfields=[
                    Subfield(code="b", value="08-17-21"),
                    Subfield(code="c", value="08-17-2021 7:50"),
                ],
            ),
            True,
            id="date",
        ),
    ],
)
def test_sierra_bib_id_missing_subfield(stub_bib, field, expectation):
    assert stub_bib.sierra_bib_id() is None


def test_sierra_bib_id_missing_value(stub_bib):
    stub_bib.add_field(
        Field(
            tag="907",
            indicators=[" ", " "],
            subfields=[Subfield(code="a", value="")],
        )
    )
    assert stub_bib.sierra_bib_id() is None


def test_sierra_bib_id_normalized(stub_bib):
    stub_bib.add_field(
        Field(
            tag="907",
            indicators=[" ", " "],
            subfields=[
                Subfield(code="a", value=".b225444884"),
                Subfield(code="b", value="08-17-21$c08-17-2021 7:50"),
            ],
        )
    )
    assert stub_bib.sierra_bib_id_normalized() == "22544488"


def test_sierra_bib_id_normalized_missing_tag(stub_bib):
    assert stub_bib.sierra_bib_id_normalized() is None


@pytest.mark.parametrize(
    "arg1,arg2,arg3,expectation",
    [
        (
            "bpl",
            "099",
            [Subfield(code="a", value="FIC"), Subfield(code="a", value="FOO")],
            "FIC FOO",
        ),
        (
            "bpl",
            "091",
            [Subfield(code="a", value="FIC"), Subfield(code="a", value="FOO")],
            None,
        ),
        (
            "nypl",
            "091",
            [Subfield(code="a", value="FIC"), Subfield(code="c", value="FOO")],
            "FIC FOO",
        ),
        (
            "nypl",
            "099",
            [Subfield(code="a", value="FIC"), Subfield(code="c", value="FOO")],
            None,
        ),
        (
            "",
            "091",
            [Subfield(code="a", value="FIC"), Subfield(code="c", value="FOO")],
            None,
        ),
    ],
)
def test_branch_call_no(stub_bib, arg1, arg2, arg3, expectation):
    stub_bib.library = arg1
    stub_bib.add_field(Field(tag=arg2, indicators=[" ", " "], subfields=arg3))
    assert stub_bib.branch_call_no() == expectation


def test_audience_missing_008(stub_bib):
    stub_bib.remove_fields("008")
    assert stub_bib.audience() is None


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
def test_audience(stub_bib, arg1, arg2, expectation):
    s = list(stub_bib.leader)
    s[6] = arg1
    s[7] = arg2
    stub_bib.leader = "".join(s)
    assert stub_bib.audience() == expectation


@pytest.mark.parametrize(
    "arg, expectation",
    [
        ("08-02-2021 16:19", datetime(2021, 8, 2).date()),
        ("12-30-2020 9:51", datetime(2020, 12, 30).date()),
        ("12-30-2022", datetime(2022, 12, 30).date()),
        ("01-30-22", datetime(2022, 1, 30).date()),
    ],
)
def test_created_date(stub_bib, arg, expectation):
    stub_bib.add_field(
        Field(
            tag="907",
            subfields=[
                Subfield(code="a", value=".b225375965"),
                Subfield(code="b", value="08-17-21"),
                Subfield(code="c", value=arg),
            ],
        )
    )
    # print(type(stub_bib.created_date()))
    assert stub_bib.created_date() == expectation


def test_cataloging_date(stub_bib):
    stub_bib.add_field(
        Field(
            tag="907",
            subfields=[
                Subfield(code="a", value=".b225375965"),
                Subfield(code="b", value="08-17-21"),
                Subfield(code="c", value="08-02-21"),
            ],
        )
    )
    assert stub_bib.cataloging_date() == datetime(2021, 8, 17).date()


def test_control_number_missing_001(stub_bib):
    assert stub_bib.control_number() is None


@pytest.mark.parametrize(
    "arg,expectation", [("ocn12345", "ocn12345"), (" 12345 ", "12345")]
)
def test_control_nubmer(arg, expectation, stub_bib):
    stub_bib.add_field(Field(tag="001", data=arg))
    assert stub_bib.control_number() == expectation


def test_record_type(stub_bib):
    assert stub_bib.record_type() == "a"


def test_physical_description_no_300_tag(stub_bib):
    assert stub_bib.physical_description() is None


@pytest.mark.parametrize(
    "tags,expectation",
    [
        (["100", "245"], "100"),
        (["110", "245"], "110"),
        (["111", "245"], "111"),
        (["245"], "245"),
    ],
)
def test_main_entry(stub_bib, tags, expectation):
    stub_bib.remove_fields("100", "245")
    for t in tags:
        stub_bib.add_field(Field(tag=t, subfields=[Subfield(code="a", value="foo")]))
    main_entry = stub_bib.main_entry()
    assert type(main_entry) is Field
    assert main_entry.tag == expectation


def test_dewey_no_082(stub_bib):
    assert stub_bib.dewey() is None


def test_dewey_lc_selected(stub_bib):
    stub_bib.add_field(
        Field(
            tag="082",
            indicators=[" ", " "],
            subfields=[Subfield(code="a", value="900./092")],
        )
    )
    stub_bib.add_field(
        Field(
            tag="082",
            indicators=["0", "4"],
            subfields=[Subfield(code="a", value="909.092")],
        )
    )
    stub_bib.add_field(
        Field(
            tag="082",
            indicators=["0", "0"],
            subfields=[Subfield(code="a", value="909.12")],
        )
    )
    assert stub_bib.dewey() == "909.12"


def test_dewey_other_agency_selected(stub_bib):
    stub_bib.add_field(
        Field(
            tag="082",
            indicators=["1", "0"],
            subfields=[Subfield(code="a", value="900")],
        )
    )
    stub_bib.add_field(
        Field(
            tag="082",
            indicators=["0", "4"],
            subfields=[Subfield(code="a", value="909./092")],
        )
    )
    assert stub_bib.dewey() == "909.092"


def test_dewey_shortened(stub_bib):
    stub_bib.add_field(
        Field(
            tag="082",
            indicators=[" ", " "],
            subfields=[Subfield(code="a", value="900.092")],
        )
    )
    stub_bib.add_field(
        Field(
            tag="082",
            indicators=["0", "4"],
            subfields=[Subfield(code="a", value="910.092")],
        )
    )
    stub_bib.add_field(
        Field(
            tag="082",
            indicators=["0", "0"],
            subfields=[Subfield(code="a", value="909./09208")],
        )
    )
    assert stub_bib.dewey_shortened() == "909.092"


def test_dewey_shortened_missing_dewey(stub_bib):
    stub_bib.add_field(
        Field(
            tag="082",
            indicators=["0", "4"],
            subfields=[Subfield(code="a", value="[FIC]")],
        )
    )
    assert stub_bib.dewey_shortened() is None


def test_languages_none_008(stub_bib):
    stub_bib.remove_fields("008")
    assert stub_bib.languages() == []


def test_languages_only_008_present(stub_bib):
    assert stub_bib.languages() == ["hat"]


def test_languages_multiple(stub_bib):
    stub_bib.add_field(
        Field(
            tag="041",
            subfields=[
                Subfield(code="a", value="eng"),
                Subfield(code="a", value="spa"),
                Subfield(code="b", value="chi"),
                Subfield(code="h", value="rus"),
            ],
        )
    )
    assert stub_bib.languages() == ["hat", "eng", "spa"]


def test_lccn_missing_010(stub_bib):
    assert stub_bib.lccn() is None


def test_lccn_missing_sub_a(stub_bib):
    stub_bib.add_field(
        Field(
            tag="010",
            indicators=[" ", " "],
            subfields=[Subfield(code="z", value="foo")],
        )
    )
    assert stub_bib.lccn() is None


@pytest.mark.parametrize(
    "arg,expectation",
    [
        ("   85153773 ", "85153773"),
        ("nuc76039265 ", "nuc76039265"),
        ("  2001627090", "2001627090"),
    ],
)
def test_lccn(arg, expectation, stub_bib):
    stub_bib.add_field(
        Field(
            tag="010",
            indicators=[" ", " "],
            subfields=[Subfield(code="a", value=arg), Subfield(code="b", value="foo")],
        )
    )
    assert stub_bib.lccn() == expectation


def test_form_of_item_not_present(stub_bib):
    stub_bib.leader = "#" * 6 + "x" + "#" * 18
    stub_bib["008"].data = "#" * 23 + "f" + "#" * 10
    assert stub_bib.form_of_item() is None


def test_form_of_item_missing_008_tag(stub_bib):
    stub_bib.remove_fields("008")
    assert stub_bib.form_of_item() is None


@pytest.mark.parametrize("arg", ["a", "c", "d", "i", "j", "m", "o", "p", "t"])
def test_form_of_item_in_pos_23(arg, stub_bib):
    stub_bib.leader = "#" * 6 + arg + "#" * 18
    stub_bib["008"].data = "#" * 23 + "f" + "#" * 10
    assert stub_bib.form_of_item() == "f"


@pytest.mark.parametrize("arg", ["e", "f", "g", "k"])
def test_form_of_item_in_pos_29(arg, stub_bib):
    stub_bib.leader = "#" * 6 + arg + "#" * 18
    stub_bib["008"].data = "#" * 29 + "o" + "#" * 14
    assert stub_bib.form_of_item() == "o"


@pytest.mark.parametrize("arg", [1, "foo"])
def test_orders_exceptions(arg, stub_bib, mock_960):
    msg = "Invalid 'sort' argument was passed."
    stub_bib.add_field(mock_960)
    with pytest.raises(BookopsMarcError) as exc:
        stub_bib.orders(sort=arg)
    assert msg in str(exc)


def test_orders_single(stub_bib, mock_960):
    stub_bib.add_field(mock_960)
    stub_bib.add_field(
        Field(
            tag="961",
            indicators=[" ", " "],
            subfields=[
                Subfield(code="h", value="e,bio"),
                Subfield(code="l", value="1643137123"),
            ],
        )
    )
    orders = stub_bib.orders()
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


def test_orders_reverse_sort(stub_bib, mock_960):
    stub_bib.add_field(mock_960)
    stub_bib.add_field(
        Field(
            tag="961",
            indicators=[" ", " "],
            subfields=[
                Subfield(code="h", value="e,bio"),
                Subfield(code="l", value="1643137123"),
            ],
        )
    )
    # add second 960 without 961
    second_960 = deepcopy(mock_960)
    second_960.delete_subfield("z")
    second_960.add_subfield("z", ".o10000020")
    stub_bib.add_field(second_960)
    orders = stub_bib.orders(sort="descending")

    assert len(orders) == 2
    assert orders[0].oid == 1000002
    assert orders[0].venNotes is None
    assert orders[1].oid == 1000001
    assert orders[1].venNotes == "e,bio"


def test_overdrive_number_missing_037(stub_bib):
    assert stub_bib.overdrive_number() is None


def test_overdrive_number_missing_sub_a(stub_bib):
    stub_bib.add_field(
        Field(
            tag="037",
            indicators=[" ", " "],
            subfields=[Subfield(code="z", value="foo")],
        )
    )
    assert stub_bib.overdrive_number() is None


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
def test_overdrive_number(arg, expectation, stub_bib):
    stub_bib.add_field(
        Field(
            tag="037",
            indicators=[" ", " "],
            subfields=[
                Subfield(code="a", value=arg),
                Subfield(code="b", value="OverDrive, Inc."),
            ],
        )
    )
    assert stub_bib.overdrive_number() == expectation


@pytest.mark.parametrize(
    "field,expectation",
    [
        pytest.param(
            Field(
                tag="650",
                indicators=[" ", "0"],
                subfields=[Subfield(code="a", value="Foo.")],
            ),
            True,
            id="regular LCSH",
        ),
        pytest.param(
            Field(
                tag="650",
                indicators=[" ", "7"],
                subfields=[
                    Subfield(code="a", value="Foo."),
                    Subfield(code="2", value="lcsh"),
                ],
            ),
            True,
            id="LCSH $2",
        ),
        pytest.param(
            Field(
                tag="650",
                indicators=[" ", "7"],
                subfields=[
                    Subfield(code="a", value="Foo."),
                    Subfield(code="2", value="fast"),
                ],
            ),
            True,
            id="fast",
        ),
        pytest.param(
            Field(
                tag="650",
                indicators=[" ", "7"],
                subfields=[
                    Subfield(code="a", value="Foo."),
                    Subfield(code="2", value="gsafd"),
                ],
            ),
            True,
            id="gsafd",
        ),
        pytest.param(
            Field(
                tag="650",
                indicators=[" ", "7"],
                subfields=[
                    Subfield(code="a", value="Foo."),
                    Subfield(code="2", value="lcgft"),
                ],
            ),
            True,
            id="lcgft",
        ),
        pytest.param(
            Field(
                tag="650",
                indicators=[" ", "7"],
                subfields=[
                    Subfield(code="a", value="Foo."),
                    Subfield(code="2", value="lctgm"),
                ],
            ),
            True,
            id="lctgm",
        ),
        pytest.param(
            Field(
                tag="650",
                indicators=[" ", "7"],
                subfields=[
                    Subfield(code="a", value="Foo."),
                    Subfield(code="2", value="bookops"),
                ],
            ),
            True,
            id="bookops",
        ),
        pytest.param(
            Field(
                tag="650",
                indicators=[" ", "7"],
                subfields=[
                    Subfield(code="a", value="Foo."),
                    Subfield(code="2", value="homoit"),
                ],
            ),
            True,
            id="homoit",
        ),
        pytest.param(
            Field(
                tag="600",
                indicators=["1", "0"],
                subfields=[Subfield(code="a", value="Foo.")],
            ),
            True,
            id="600 LCSH tag",
        ),
        pytest.param(
            Field(
                tag="610",
                indicators=[" ", "0"],
                subfields=[Subfield(code="a", value="Foo.")],
            ),
            True,
            id="610 LCSH tag",
        ),
        pytest.param(
            Field(
                tag="611",
                indicators=[" ", "0"],
                subfields=[Subfield(code="a", value="Foo.")],
            ),
            True,
            id="611 LCSH tag",
        ),
        pytest.param(
            Field(
                tag="630",
                indicators=[" ", "0"],
                subfields=[Subfield(code="a", value="Foo.")],
            ),
            True,
            id="630 LCSH tag",
        ),
        pytest.param(
            Field(
                tag="648",
                indicators=[" ", "0"],
                subfields=[Subfield(code="a", value="Foo.")],
            ),
            True,
            id="648 LCSH tag",
        ),
        pytest.param(
            Field(
                tag="650",
                indicators=[" ", "0"],
                subfields=[Subfield(code="a", value="Foo.")],
            ),
            True,
            id="650 LCSH tag",
        ),
        pytest.param(
            Field(
                tag="651",
                indicators=[" ", "0"],
                subfields=[Subfield(code="a", value="Foo.")],
            ),
            True,
            id="651 LCSH tag",
        ),
        pytest.param(
            Field(
                tag="655",
                indicators=[" ", "0"],
                subfields=[Subfield(code="a", value="Foo.")],
            ),
            True,
            id="655 LCSH tag",
        ),
        pytest.param(
            Field(
                tag="650",
                indicators=[" ", "7"],
                subfields=[
                    Subfield(code="a", value="Foo."),
                    Subfield(code="2", value="aat"),
                ],
            ),
            False,
            id="att",
        ),
        pytest.param(
            Field(
                tag="650",
                indicators=[" ", "1"],
                subfields=[Subfield(code="a", value="Foo.")],
            ),
            False,
            id="Children's LCSH",
        ),
        pytest.param(
            Field(
                tag="654",
                indicators=[" ", "0"],
                subfields=[Subfield(code="a", value="Foo.")],
            ),
            False,
            id="654 tag",
        ),
        pytest.param(
            Field(
                tag="690",
                indicators=[" ", "0"],
                subfields=[Subfield(code="a", value="Foo.")],
            ),
            False,
            id="690 tag",
        ),
        pytest.param(
            Field(
                tag="650",
                indicators=[" ", "7"],
                subfields=[Subfield(code="a", value="Foo.")],
            ),
            False,
            id="Invalid ind2",
        ),
    ],
)
def test_remove_unsupported_subjects(stub_bib, field, expectation):
    stub_bib.add_field(field)
    stub_bib.remove_unsupported_subjects()
    (field.tag in stub_bib) == expectation


def test_subjects_lc(stub_bib):
    stub_bib.add_field(
        Field(
            tag="650",
            indicators=[" ", "7"],
            subfields=[
                Subfield(code="a", value="Foo"),
                Subfield(code="2", value="bar"),
            ],
        )
    )
    stub_bib.add_field(
        Field(
            tag="600",
            indicators=["1", "0"],
            subfields=[
                Subfield(code="a", value="Doe, John"),
                Subfield(code="x", value="Childhood."),
            ],
        )
    )
    stub_bib.add_field(
        Field(
            tag="650",
            indicators=[" ", "4"],
            subfields=[
                Subfield(code="a", value="Foo"),
                Subfield(code="2", value="bar"),
            ],
        )
    )
    stub_bib.add_field(
        Field(
            tag="651",
            indicators=[" ", "0"],
            subfields=[Subfield(code="a", value="Spam.")],
        )
    )
    lc_subjects = stub_bib.subjects_lc()
    assert len(lc_subjects) == 2
    assert lc_subjects[0].subfields == [
        Subfield(code="a", value="Doe, John"),
        Subfield(code="x", value="Childhood."),
    ]
    assert lc_subjects[1].subfields == [Subfield(code="a", value="Spam.")]


def test_suppressed_missing_998(stub_bib):
    assert stub_bib.suppressed() is False


def test_suppressed_missing_998_e(stub_bib):
    stub_bib.add_field(Field(tag="998", subfields=[Subfield(code="a", value="foo")]))
    assert stub_bib.suppressed() is False


@pytest.mark.parametrize(
    "arg,expectation",
    [
        ("-", False),
        ("a", False),
        ("c", True),
        ("e", True),
        ("n", True),
        ("q", True),
        ("o", True),
        ("v", True),
    ],
)
def test_suppressed(stub_bib, arg, expectation):
    stub_bib.add_field(Field(tag="998", subfields=[Subfield(code="e", value=arg)]))
    assert stub_bib.suppressed() == expectation


def test_upc_number_missing_024(stub_bib):
    assert stub_bib.upc_number() is None


def test_upc_number_missing_sub_a(stub_bib):
    stub_bib.add_field(
        Field(
            tag="024",
            indicators=["1", " "],
            subfields=[Subfield(code="z", value="foo")],
        )
    )
    assert stub_bib.upc_number() is None


def test_upc_number_other_number(stub_bib):
    stub_bib.add_field(
        Field(
            tag="024",
            indicators=["2", " "],
            subfields=[
                Subfield(code="a", value="M011234564"),
                Subfield(code="z", value="foo"),
            ],
        )
    )
    assert stub_bib.upc_number() is None


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
def test_upc_number(arg, expectation, stub_bib):
    stub_bib.add_field(
        Field(
            tag="024",
            indicators=["1", " "],
            subfields=[Subfield(code="a", value=arg), Subfield(code="b", value="foo")],
        )
    )
    assert stub_bib.upc_number() == expectation


@pytest.mark.parametrize("arg", ["bpl", "nypl", None])
def test_instating_from_pymarc_record(stub_pymarc_record, arg):
    bib = pymarc_record_to_local_bib(stub_pymarc_record, arg)
    assert isinstance(bib, Bib)

    # bib atributes
    assert bib.library == arg

    # bib methods
    assert str(bib.main_entry()) == "=100  1\\$aAdams, John,$eauthor."


def test_flat_dict(stub_bib):
    flattened = stub_bib.flat_dict()
    assert flattened == {
        "leader": "02866pam  2200517 i 4500",
        "008": "190306s2017    ht a   j      000 1 hat d",
        "100": {
            "ind1": "1",
            "ind2": " ",
            "subfields": [{"a": "Adams, John,"}, {"e": "author."}],
        },
        "245": {
            "ind1": "1",
            "ind2": "4",
            "subfields": [{"a": "The foo /"}, {"c": "by John Adams."}],
        },
        "264": {
            "ind1": " ",
            "ind2": "1",
            "subfields": [{"a": "Bar :"}, {"b": "New York,"}, {"c": "2021"}],
        },
    }
