import io
from pymarc.exceptions import (
    TruncatedRecord,
    RecordLengthInvalid,
    EndOfRecordNotFound,
)
from bookops_marc import SierraBibReader


def test_SierraBibReader():
    with open("tests/nyp-sample.mrc", "rb") as fh:
        file = fh.read()
    reader = SierraBibReader(file, library="nypl", hide_utf8_warnings=True)
    assert reader.current_chunk is None
    assert reader.current_exception is None
    assert reader.file_handle is not None
    assert isinstance(reader.file_handle, io.BytesIO)
    assert reader.file_handle.read(5) == b"02866"


class TestSierraBibReaderIteration:
    def test_SierraBibReader(self):
        with open("tests/nyp-sample.mrc", "rb") as marcfile:
            reader = SierraBibReader(marcfile, library="nypl", hide_utf8_warnings=True)
            n = 0
            for bib in reader:
                n += 1
            assert n == 9

    def test_SierraBibReader_TruncatedRecord_too_short(self):
        bib = bytes("0123", "utf-8")
        reader = SierraBibReader(bib, library="nypl")
        for record in reader:
            assert record is None
        assert isinstance(reader.current_exception, TruncatedRecord)

    def test_SierraBibReader_RecordLengthInvalid(self):
        bib = bytes(
            "pam a2200073 i 4500008004100000100002600041245003000067264002700097",
            "utf-8",
        )
        assert isinstance(bib, bytes)
        reader = SierraBibReader(bib, library="nypl")
        for record in reader:
            pass
        assert isinstance(reader.current_exception, RecordLengthInvalid)

    def test_SierraBibReader_TruncatedRecord_leader_len_incorrect(self):
        bib = bytes(
            "99999pam a2200517 i 4500008004100000100002600041245003000067264002700097",
            "utf-8",
        )
        assert isinstance(bib, bytes)
        reader = SierraBibReader(bib, library="nypl")
        for record in reader:
            pass
        assert isinstance(reader.current_exception, TruncatedRecord)

    def test_SierraBibReader_EndOfRecordNotFound(self):
        bib = b"00006 "
        assert isinstance(bib, bytes)
        reader = SierraBibReader(bib, library="nypl", hide_utf8_warnings=True)
        for record in reader:
            assert record is None
        assert reader.current_exception is not None
        assert isinstance(reader.current_exception, EndOfRecordNotFound)

    def test_SierraBibReader_exception_bib_init(self):
        bibs = b"00198pam a2200-73 i 4500008004100000100002600041245003000067264002700097\x1e190306s2017    ht a   j      000 1 hat d\x1e1 \x1faAdams, John,\x1feauthor.\x1e14\x1faThe foo /\x1fcby John Adams.\x1e 1\x1faBar :\x1fbNew York,\x1fc2021\x1e\x1d"  # noqa: E501
        assert isinstance(bibs, bytes)
        reader = SierraBibReader(bibs, library="nypl")
        for record in reader:
            assert reader.current_exception is not None
        assert reader.current_exception is None
