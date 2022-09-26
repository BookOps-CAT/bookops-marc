"""
Tests bib.py module
"""
from contextlib import nullcontext as does_not_raise
from copy import deepcopy
from datetime import datetime

import pytest

from pymarc import Field

from bookops_marc.bib import (
    Bib,
    normalize_dewey,
    shorten_dewey,
    pymarc_record_to_local_bib,
)
from bookops_marc.errors import BookopsMarcError
from bookops_marc.order import Order


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


def test_audience_missing_008(stub_bib):
    stub_bib.remove_fields("008")
    assert stub_bib.audience() is None


@pytest.mark.parametrize("arg", [None, "foo", 123])
def test_bib_invalid_library_arg(arg):
    with pytest.raises(ValueError) as exc:
        Bib(library=arg)

    assert "Invalid 'library' argument passed. Must be a library code as str." in str(
        exc.value
    )


@pytest.mark.parametrize("arg", ["BPL", "bpl", "NYPL", "nypl"])
def test_bib_blank_record(arg):
    with does_not_raise():
        Bib(library=arg)


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
def test_branch_call_no(stub_bib, arg1, arg2, arg3, expectation):
    stub_bib.library = arg1
    stub_bib.add_field(Field(tag=arg2, indicators=[" ", " "], subfields=arg3))
    assert stub_bib.branch_call_no() == expectation


def test_cataloging_date(stub_bib):
    stub_bib.add_field(
        Field(
            tag="907",
            subfields=["a", ".b225375965", "b", "08-17-21", "c", "08-02-21"],
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
            subfields=["a", ".b225375965", "b", "08-17-21", "c", arg],
        )
    )
    # print(type(stub_bib.created_date()))
    assert stub_bib.created_date() == expectation


def test_dewey_no_082(stub_bib):
    assert stub_bib.dewey() is None


def test_dewey_lc_selected(stub_bib):
    stub_bib.add_field(
        Field(tag="082", indicators=[" ", " "], subfields=["a", "900./092"])
    )
    stub_bib.add_field(
        Field(tag="082", indicators=["0", "4"], subfields=["a", "909.092"])
    )
    stub_bib.add_field(
        Field(tag="082", indicators=["0", "0"], subfields=["a", "909.12"])
    )
    assert stub_bib.dewey() == "909.12"


def test_dewey_other_agency_selected(stub_bib):
    stub_bib.add_field(Field(tag="082", indicators=["1", "0"], subfields=["a", "900"]))
    stub_bib.add_field(
        Field(tag="082", indicators=["0", "4"], subfields=["a", "909./092"])
    )
    assert stub_bib.dewey() == "909.092"


def test_dewey_shortened(stub_bib):
    stub_bib.add_field(
        Field(tag="082", indicators=[" ", " "], subfields=["a", "900.092"])
    )
    stub_bib.add_field(
        Field(tag="082", indicators=["0", "4"], subfields=["a", "910.092"])
    )
    stub_bib.add_field(
        Field(tag="082", indicators=["0", "0"], subfields=["a", "909./09208"])
    )
    assert stub_bib.dewey_shortened() == "909.092"


def test_dewey_shortened_missing_dewey(stub_bib):
    stub_bib.add_field(
        Field(tag="082", indicators=["0", "4"], subfields=["a", "[FIC]"])
    )
    assert stub_bib.dewey_shortened() is None


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


@pytest.mark.parametrize("arg", ["bpl", "nypl"])
def test_instating_from_pymarc_record(stub_pymarc_record, arg):
    bib = pymarc_record_to_local_bib(stub_pymarc_record, arg)
    assert isinstance(bib, Bib)

    # bib atributes
    assert bib.library == arg

    # bib methods
    assert str(bib.main_entry()) == "=100  1\\$aAdams, John,$eauthor."


def test_instating_from_pymarc_record_no_library_specified(stub_pymarc_record):
    with pytest.raises(ValueError) as exc:
        pymarc_record_to_local_bib(stub_pymarc_record, None)


def test_languages_none_008(stub_bib):
    stub_bib.remove_fields("008")
    assert stub_bib.languages() == []


def test_languages_only_008_present(stub_bib):
    assert stub_bib.languages() == ["hat"]


def test_languages_multiple(stub_bib):
    stub_bib.add_field(
        Field(tag="041", subfields=["a", "eng", "a", "spa", "b", "chi", "h", "rus"])
    )
    assert stub_bib.languages() == ["hat", "eng", "spa"]


def test_lccn_missing_010(stub_bib):
    assert stub_bib.lccn() is None


def test_lccn_missing_sub_a(stub_bib):
    stub_bib.add_field(Field(tag="010", indicators=[" ", " "], subfields=["z", "foo"]))
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
        Field(tag="010", indicators=[" ", " "], subfields=["a", arg, "b", "foo"])
    )
    assert stub_bib.lccn() == expectation


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
        stub_bib.add_field(Field(tag=t, subfields=["a", "foo"]))
    main_entry = stub_bib.main_entry()
    assert type(main_entry) == Field
    assert main_entry.tag == expectation


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


@pytest.mark.parametrize("arg", [1, "foo"])
def test_orders_exceptions(arg, stub_bib, stub_960):
    msg = "Invalid 'sort' argument was passed."
    stub_bib.add_field(stub_960)
    with pytest.raises(BookopsMarcError) as exc:
        stub_bib.orders(sort=arg)
    assert msg in str(exc)


def test_orders_single(stub_bib, stub_960, stub_961):
    stub_bib.library = "BPL"
    stub_bib.add_field(stub_960)
    stub_bib.add_field(stub_961)
    orders = stub_bib.orders()
    assert len(orders) == 1
    o = orders[0]
    assert isinstance(o, Order)


def test_orders_reverse_sort(stub_bib, stub_960, stub_961):
    # first order tags pair
    stub_bib.library = "BPL"
    stub_bib.add_field(stub_960)
    stub_bib.add_field(stub_961)

    # second order tags pair
    second_960 = deepcopy(stub_960)
    second_960.delete_subfield("z")
    second_960.add_subfield("z", ".o10000020")
    stub_bib.add_field(second_960)

    orders = stub_bib.orders(sort="descending")

    assert len(orders) == 2
    assert orders[0].oid == 1000002
    assert orders[0].vendorNotes is ()
    assert orders[1].oid == 1000001
    assert isinstance(orders[1].vendorNotes, tuple)


def test_overdrive_number_missing_037(stub_bib):
    assert stub_bib.overdrive_number() is None


def test_overdrive_number_missing_sub_a(stub_bib):
    stub_bib.add_field(Field(tag="037", indicators=[" ", " "], subfields=["z", "foo"]))
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
            subfields=["a", arg, "b", "OverDrive, Inc."],
        )
    )
    assert stub_bib.overdrive_number() == expectation


def test_physical_description_no_300_tag(stub_bib):
    assert stub_bib.physical_description() is None


def test_record_type(stub_bib):
    assert stub_bib.record_type() == "a"


@pytest.mark.parametrize(
    "field,expectation",
    [
        pytest.param(
            Field(tag="650", indicators=[" ", "0"], subfields=["a", "Foo."]),
            True,
            id="regular LCSH",
        ),
        pytest.param(
            Field(
                tag="650", indicators=[" ", "7"], subfields=["a", "Foo.", "2", "lcsh"]
            ),
            True,
            id="LCSH $2",
        ),
        pytest.param(
            Field(
                tag="650", indicators=[" ", "7"], subfields=["a", "Foo.", "2", "fast"]
            ),
            True,
            id="fast",
        ),
        pytest.param(
            Field(
                tag="650", indicators=[" ", "7"], subfields=["a", "Foo.", "2", "gsafd"]
            ),
            True,
            id="gsafd",
        ),
        pytest.param(
            Field(
                tag="650", indicators=[" ", "7"], subfields=["a", "Foo.", "2", "lcgft"]
            ),
            True,
            id="lcgft",
        ),
        pytest.param(
            Field(
                tag="650", indicators=[" ", "7"], subfields=["a", "Foo.", "2", "lctgm"]
            ),
            True,
            id="lctgm",
        ),
        pytest.param(
            Field(
                tag="650",
                indicators=[" ", "7"],
                subfields=["a", "Foo.", "2", "bookops"],
            ),
            True,
            id="bookops",
        ),
        pytest.param(
            Field(
                tag="650", indicators=[" ", "7"], subfields=["a", "Foo.", "2", "homoit"]
            ),
            True,
            id="homoit",
        ),
        pytest.param(
            Field(tag="600", indicators=["1", "0"], subfields=["a", "Foo."]),
            True,
            id="600 LCSH tag",
        ),
        pytest.param(
            Field(tag="610", indicators=[" ", "0"], subfields=["a", "Foo."]),
            True,
            id="610 LCSH tag",
        ),
        pytest.param(
            Field(tag="611", indicators=[" ", "0"], subfields=["a", "Foo."]),
            True,
            id="611 LCSH tag",
        ),
        pytest.param(
            Field(tag="630", indicators=[" ", "0"], subfields=["a", "Foo."]),
            True,
            id="630 LCSH tag",
        ),
        pytest.param(
            Field(tag="648", indicators=[" ", "0"], subfields=["a", "Foo."]),
            True,
            id="648 LCSH tag",
        ),
        pytest.param(
            Field(tag="650", indicators=[" ", "0"], subfields=["a", "Foo."]),
            True,
            id="650 LCSH tag",
        ),
        pytest.param(
            Field(tag="651", indicators=[" ", "0"], subfields=["a", "Foo."]),
            True,
            id="651 LCSH tag",
        ),
        pytest.param(
            Field(tag="655", indicators=[" ", "0"], subfields=["a", "Foo."]),
            True,
            id="655 LCSH tag",
        ),
        pytest.param(
            Field(
                tag="650", indicators=[" ", "7"], subfields=["a", "Foo.", "2", "aat"]
            ),
            False,
            id="att",
        ),
        pytest.param(
            Field(tag="650", indicators=[" ", "1"], subfields=["a", "Foo."]),
            False,
            id="Children's LCSH",
        ),
        pytest.param(
            Field(tag="654", indicators=[" ", "0"], subfields=["a", "Foo."]),
            False,
            id="654 tag",
        ),
        pytest.param(
            Field(tag="690", indicators=[" ", "0"], subfields=["a", "Foo."]),
            False,
            id="690 tag",
        ),
        pytest.param(
            Field(tag="650", indicators=[" ", "7"], subfields=["a", "Foo."]),
            False,
            id="Invalid ind2",
        ),
    ],
)
def test_remove_unsupported_subjects(stub_bib, field, expectation):
    stub_bib.add_field(field)
    stub_bib.remove_unsupported_subjects()
    (field.tag in stub_bib) == expectation


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


def test_sierra_bib_format_missing_tag(stub_bib):
    assert stub_bib.sierra_bib_format() is None


def test_sierra_bib_format_missing_subfield(stub_bib):
    stub_bib.add_field(Field(tag="998", subfields=["a", "foo"]))
    assert stub_bib.sierra_bib_format() is None


def test_sierra_bib_format(stub_bib):
    stub_bib.add_field(Field(tag="998", subfields=["a", "foo", "d", "x  "]))
    assert stub_bib.sierra_bib_format() == "x"


def test_sierra_bib_id_missing_tag(stub_bib):
    assert stub_bib.sierra_bib_id() is None


def test_sierra_bib_id_missing_subfield(stub_bib):
    stub_bib.add_field(
        Field(
            tag="907",
            indicators=[" ", " "],
            subfields=["b", "08-17-21$c08-17-2021 7:50"],
        )
    )
    assert stub_bib.sierra_bib_id() is None


def test_sierra_bib_id(stub_bib):
    stub_bib.add_field(
        Field(
            tag="907",
            indicators=[" ", " "],
            subfields=["a", ".b225444884", "b", "08-17-21$c08-17-2021 7:50"],
        )
    )
    assert stub_bib.sierra_bib_id() == "b225444884"


def test_sierra_bib_id_missing_tag(stub_bib):
    assert stub_bib.sierra_bib_id() is None


def test_sierra_bib_id_missing_subfield(stub_bib):
    stub_bib.add_field(
        Field(
            tag="907",
            indicators=[" ", " "],
            subfields=["b", "spam"],
        )
    )
    assert stub_bib.sierra_bib_id() is None


def test_sierra_bib_id_missing_value(stub_bib):
    stub_bib.add_field(
        Field(
            tag="907",
            indicators=[" ", " "],
            subfields=["a", ""],
        )
    )
    assert stub_bib.sierra_bib_id() is None


def test_sierra_bib_id_normalized(stub_bib):
    stub_bib.add_field(
        Field(
            tag="907",
            indicators=[" ", " "],
            subfields=["a", ".b225444884", "b", "08-17-21$c08-17-2021 7:50"],
        )
    )
    assert stub_bib.sierra_bib_id_normalized() == "22544488"


def test_sierra_bib_id_normalized_missing_tag(stub_bib):
    assert stub_bib.sierra_bib_id_normalized() is None


def test_subjects_lc(stub_bib):
    stub_bib.add_field(
        Field(tag="650", indicators=[" ", "7"], subfields=["a", "Foo", "2", "bar"])
    )
    stub_bib.add_field(
        Field(
            tag="600",
            indicators=["1", "0"],
            subfields=["a", "Doe, John", "x", "Childhood."],
        )
    )
    stub_bib.add_field(
        Field(tag="650", indicators=[" ", "4"], subfields=["a", "Foo", "2", "bar"])
    )
    stub_bib.add_field(
        Field(tag="651", indicators=[" ", "0"], subfields=["a", "Spam."])
    )
    lc_subjects = stub_bib.subjects_lc()
    assert len(lc_subjects) == 2
    assert lc_subjects[0].subfields == ["a", "Doe, John", "x", "Childhood."]
    assert lc_subjects[1].subfields == ["a", "Spam."]


def test_suppressed_missing_998(stub_bib):
    assert stub_bib.suppressed() is False


def test_suppressed_missing_998_e(stub_bib):
    stub_bib.add_field(Field(tag="998", subfields=["a", "foo"]))
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
    stub_bib.add_field(Field(tag="998", subfields=["e", arg]))
    assert stub_bib.suppressed() == expectation


def test_upc_number_missing_024(stub_bib):
    assert stub_bib.upc_number() is None


def test_upc_number_missing_sub_a(stub_bib):
    stub_bib.add_field(Field(tag="024", indicators=["1", " "], subfields=["z", "foo"]))
    assert stub_bib.upc_number() is None


def test_upc_number_other_number(stub_bib):
    stub_bib.add_field(
        Field(
            tag="024", indicators=["2", " "], subfields=["a", "M011234564", "z", "foo"]
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
            subfields=["a", arg, "b", "foo"],
        )
    )
    assert stub_bib.upc_number() == expectation
