# -*- coding: utf-8 -*-

"""
Module replaces pymarc's Record module. Inherits all Record class functinality and
adds some syntactic sugar.
"""
from datetime import date
from typing import Dict, List, Optional, Union

from pymarc import Record, Field, Indicators
from pymarc.constants import LEADER_LEN

from .errors import BookopsMarcError
from .local_values import (
    OclcNumber,
    normalize_date,
    normalize_dewey,
    shorten_dewey,
)
from .models import Order
from .constants import SUPPORTED_THESAURI, SUPPORTED_SUBJECT_TAGS


class Bib(Record):
    """
    A class for representing local MARC record.
    """

    def __init__(
        self,
        data: str = "",
        library: str = "",
        to_unicode: bool = True,
        force_utf8: bool = False,
        hide_utf8_warnings: bool = False,
        utf8_handling: str = "strict",
        leader: str = " " * LEADER_LEN,
        file_encoding: str = "iso8859-1",
    ) -> None:
        super().__init__(
            data,
            to_unicode,
            force_utf8,
            hide_utf8_warnings,
            utf8_handling,
            leader,
            file_encoding,
        )

        if isinstance(library, str):
            self.library = library.lower()
        else:
            self.library = library

    def __iter__(self):
        self.pos = 0
        return self

    def __next__(self):
        if self.pos >= len(self.fields):
            raise StopIteration
        self.pos += 1
        return self.fields[self.pos - 1]

    def audience(self) -> Optional[str]:
        """
        Retrieves audience code from the 008 MARC tag
        """
        try:
            if self.leader[6] in "acdgijkmt" and self.leader[7] in "am":
                return self.get("008").data[22]  # type: ignore
            else:
                return None
        except AttributeError:
            return None

    def branch_call_no(self) -> Optional[str]:
        """
        Retrieves branch library call number as string without any MARC coding
        """
        field = self.branch_call_no_field()
        try:
            return field.value()  # type:ignore
        except AttributeError:
            return None

    def branch_call_no_field(self) -> Optional[Field]:
        """
        Retrieves a branch library call number field as pymarc.Field instance
        """
        if self.library == "bpl":
            return self.get("099")
        elif self.library == "nypl":
            return self.get("091")
        else:
            return None

    def cataloging_date(self) -> Optional[date]:
        """
        Extracts cataloging date from the bib
        """
        try:
            cat_date = normalize_date(self.get("907").get(code="b"))  # type: ignore
            return cat_date
        except AttributeError:
            return None

    def control_number(self) -> Optional[str]:
        """
        Returns a control number from the 001 tag if exists.
        """
        try:
            return self.get("001").data.strip()  # type: ignore
        except AttributeError:
            return None

    def created_date(self) -> Optional[date]:
        """
        Extracts bib creation date
        """
        try:
            created_date = normalize_date(self.get("907").get(code="c"))  # type: ignore
            return created_date
        except AttributeError:
            return None

    def dewey(self) -> Optional[str]:
        """
        Returns LC suggested Dewey classification then other agency's number.
        Does not alter the class mark string.
        """
        fields = self.get_fields("082")

        # check if LC full ed. present first
        for field in fields:
            if field.indicators == Indicators("0", "0"):
                class_mark = field.get(code="a").strip()
                class_mark = normalize_dewey(class_mark)
                return class_mark  # type: ignore

        # then other agency full ed.
        for field in fields:
            if field.indicators == Indicators("0", "4"):
                class_mark = field.get(code="a").strip()
                class_mark = normalize_dewey(class_mark)
                return class_mark  # type: ignore

        return None

    def dewey_shortened(self) -> Optional[str]:
        """
        Returns LC suggested Dewey classification then other agency's number
        if present .
        """
        class_mark = self.dewey()
        if isinstance(class_mark, str):
            return shorten_dewey(class_mark)
        else:
            return None

    def form_of_item(self) -> Optional[str]:
        """
        Returns form of item code from the 008 tag position 23 if applicable for
        a given material format
        """
        rec_type = self.record_type()

        if isinstance(rec_type, str) and "008" in self:
            if rec_type in "acdijmopt":
                return self.get("008").data[23]  # type: ignore
            elif rec_type in "efgk":
                return self.get("008").data[29]  # type: ignore
            else:
                return None
        else:
            return None

    def languages(self) -> List[str]:
        """
        Returns list of material main languages
        """
        languages = []

        try:
            languages.append(self.get("008").data[35:38])  # type: ignore
        except AttributeError:
            pass

        for field in self.get_fields("041"):
            for sub in field.get_subfields("a"):
                languages.append(sub)
        return languages

    def lccn(self) -> Optional[str]:
        """
        Returns Library of Congress Control Number
        """
        try:
            return self.get("010").get(code="a").strip()  # type: ignore
        except (AttributeError, TypeError):
            return None

    def main_entry(self) -> Optional[Field]:
        """
        Returns main entry field instance
        """
        entry_fields = ["100", "110", "111", "245"]
        for field in entry_fields:
            if bool(self.get(field)):
                return self.get(field)
        else:
            raise BookopsMarcError("Incomplete MARC record: missing the main entry.")

    def normalize_oclc_control_number(self) -> None:
        """
        Enforces practices of recording OCLC prefix (BPL) or not (NYPL) in
        the 001 control field. This method updates the 001 field if it is
        an OCLC number applicable and does not return a value.
        """
        if self.library not in ["nypl", "bpl"]:
            raise BookopsMarcError(
                "Not defined library argument to apply the correct practice."
            )
        controlNo = self.control_number()
        if not controlNo or not OclcNumber.is_valid(controlNo):
            pass
        elif self.library == "bpl":
            self["001"].data = OclcNumber(controlNo).with_prefix
        elif OclcNumber.is_valid(controlNo) and self.library == "nypl":
            self["001"].data = OclcNumber(controlNo).without_prefix

    def oclc_nos(self) -> Dict[str, str]:
        """
        Returns dictionary of MARC tags and OCLC identifiers found in a bib.
        Output contains the 001 if the record source, from the 003 field,
        is OCoLC, the first 035$a if it exists, and, for NYPL records, the
        first 991$y if it exists. Returns an empty dictionary if a valid OCLC
        number is not found in any of these fields.
        """
        unique_oclcs = {}

        def get_subvalue(
            fields: List[Field], subfield_code: str
        ) -> Union[OclcNumber, None]:
            for field in fields:
                value = field.get(subfield_code)
                if value and OclcNumber.is_valid(value):
                    return OclcNumber(value)
            return None

        # get OCLC #s from 001
        source_field = self.get("003")
        if source_field and "ocolc" in source_field.value().lower():
            id_field = self.get("001")
            field_value = id_field.value() if id_field is not None else None
            if field_value and OclcNumber.is_valid(field_value):
                unique_oclcs["001"] = OclcNumber(field_value).without_prefix

        # get OCLC #s from 035
        subfield_035 = get_subvalue(self.get_fields("035"), "a")
        if subfield_035 and subfield_035.has_prefix:
            unique_oclcs["035"] = subfield_035.without_prefix

        # get OCLC #s from 991
        subfield_991 = get_subvalue(self.get_fields("991"), "y")
        if subfield_991 and self.library == "nypl":
            unique_oclcs["991"] = subfield_991.without_prefix

        return unique_oclcs

    def orders(self, sort: str = "descending") -> List[Order]:
        """
        Returns a list of orders attached to bib. Order data coded in the 960 tag
        (order fixed fields) may be followed by a related 961 tag (order variable
        fields) so iterating over the entire bib is needed to connect the two
        fields. It is possible that the 960 tag may not have a related 961 (BPL).

        Args:
            sort:
                How to sort a record's orders:
                 - ascending (from oldest to most recent), or
                 - descending (from most recent to oldest)
        """

        if not isinstance(sort, str) or sort not in "ascending,descending":
            raise BookopsMarcError("Invalid 'sort' argument was passed.")

        orders = []

        for field in self:
            if field.tag == "960":
                try:
                    following_field = self.fields[self.pos]
                except IndexError:
                    following_field = None
                orders.append(Order(field, following_field))

        if sort == "descending":
            orders.reverse()

        return orders

    def overdrive_number(self) -> Optional[str]:
        """
        Returns Overdrive Reserve ID parsed from the 037 tag.
        """
        try:
            return self.get("037").get(code="a").strip()  # type: ignore
        except (AttributeError, TypeError):
            return None

    def remove_unsupported_subjects(self) -> None:
        """
        Deletes subject fields from the record that contain
        unsupported by BPL or NYPL thesauri
        """
        subjects = self.subjects

        for field in subjects:
            if field.tag not in SUPPORTED_SUBJECT_TAGS:
                self.remove_field(field)
                continue
            if field.indicator2 == "0":  # LCSH
                continue
            if field.indicator2 == "7":
                if "2" in field:
                    if field.get(code="2").strip() in SUPPORTED_THESAURI:
                        continue
                    else:
                        self.remove_field(field)
                else:
                    self.remove_field(field)
            else:
                self.remove_field(field)

    def physical_description(self) -> Optional[str]:
        """
        Returns value of the first 300 MARC tag in the bib
        """
        try:
            return self.physicaldescription()[0].value()  # type: ignore
        except (TypeError, IndexError):
            return None

    def record_type(self) -> Optional[str]:
        """
        Retrieves record type code from MARC leader
        """
        return self.leader[6]  # type: ignore

    def sierra_bib_format(self) -> Optional[str]:
        """
        Returns Sierra bib format fixed field code
        """
        try:
            return self.get("998").get(code="d").strip()  # type: ignore
        except (TypeError, AttributeError):
            return None

    def sierra_bib_id(self) -> Optional[str]:
        """
        Retrieves Sierra bib # from the 907 MARC tag
        """
        try:
            bib_id = self.get("907").get(code="a")[1:]  # type: ignore
        except (TypeError, AttributeError):
            return None

        if bib_id:
            return bib_id  # type: ignore
        else:
            return None

    def sierra_bib_id_normalized(self) -> Optional[str]:
        """
        Retrieves Sierra bib # from the 907 tag and returns it
        without 'b' prefix and the check digit.
        """
        try:
            return self.sierra_bib_id()[1:-1]  # type: ignore
        except TypeError:
            return None

    def subjects_lc(self) -> List[Field]:
        """
        Retrieves Library of Congress Subject Headings from the bib
        """
        lc_subjects = []
        for field in self.subjects:
            if field.indicator2 == "0":
                lc_subjects.append(field)
        return lc_subjects

    def suppressed(self) -> bool:
        """
        Determines based on 998 $e value if bib is suppressed from public display
        BPL usage: "c", "n"
        NYPL usage: "c", "e", "n", "q", "o", "v"
        """
        try:
            code = self.get("998").get(code="e")  # type: ignore
        except (TypeError, AttributeError):
            return False

        if code in ("c", "e", "n", "q", "o", "v"):
            return True
        else:
            return False

    def upc_number(self) -> Optional[str]:
        """
        Returns a UPC number if present on the bib.
        https://www.loc.gov/marc/bibliographic/bd024.html
        """
        tag = self.get("024")
        if tag:
            if tag.indicator1 == "1":
                try:
                    return tag.get(code="a").strip()  # type: ignore
                except AttributeError:
                    pass
        return None


def pymarc_record_to_local_bib(record: Record, library: str) -> Optional[Bib]:
    """
    Converts an instance of `pymarc.Record` to `bookops_marc.Bib`

    Args:
        record:                 `pymarc.Record` instance
        library:                'bpl' or 'nypl'

    Returns:
        `bookops_marc.bib.Bib` instance
    """
    if isinstance(record, Record):
        bib = Bib(library=library)
        bib.leader = record.leader
        bib.fields = record.fields[:]
        return bib
    else:
        return None
