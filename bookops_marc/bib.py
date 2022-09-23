# -*- coding: utf-8 -*-

"""
Module replaces pymarc's Record module. Inherits all Record class functinality and
adds some syntactic sugar.
"""
from collections import namedtuple
from datetime import datetime, date
from typing import List, Optional

from pymarc import Record, Field
from pymarc.constants import LEADER_LEN

from bookops_marc.constants import SUPPORTED_THESAURI, SUPPORTED_SUBJECT_TAGS
from bookops_marc.errors import BookopsMarcError
from bookops_marc.order import Order
from bookops_marc.utils import sierra_str2date


def normalize_dewey(class_mark: str) -> Optional[str]:
    """
    Normalizes Dewey classification to be used in call numbers

    Args:
        class_mark:                  Dewey classification

    Returns:
        normalized class_mark
    """
    if isinstance(class_mark, str):
        class_mark = (
            class_mark.replace("/", "")
            .replace("j", "")
            .replace("C", "")
            .replace("[B]", "")
            .replace("'", "")
            .strip()
        )
        try:
            float(class_mark)
        except ValueError:
            return None
        else:
            while len(class_mark) > 4 and class_mark[-1] == "0":
                class_mark = class_mark[:-1]
            return class_mark
    else:
        return None


def shorten_dewey(class_mark: str, digits_after_period: int = 4) -> str:
    """
    Shortens Dewey classification number to maximum 4 digits after period.
    BPL materials: default 4 digits - 505.4167
    NYPl adult/young adult: default 4 digits
    NYPL juvenile materials:    2 digits - 618.54

    Args:
        class_mark:                 Dewey classification
        digits_after_period:        number of allowed digits after period

    Returns:
        shortened class_mark

    """
    class_mark = class_mark[: 4 + digits_after_period]
    while len(class_mark) > 3 and class_mark[-1] in ".0":
        class_mark = class_mark[:-1]
    return class_mark


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
                return self["008"].data[22]  # type: ignore
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
            return self["099"]
        elif self.library == "nypl":
            return self["091"]
        else:
            return None

    def cataloging_date(self) -> Optional[date]:
        """
        Extracts cataloging date from the bib
        """
        cat_date = sierra_str2date(self["907"]["b"])
        return cat_date

    def control_number(self) -> Optional[str]:
        """
        Returns a control number from the 001 tag if exists.
        """
        try:
            return self["001"].data.strip()  # type: ignore
        except AttributeError:
            return None

    def created_date(self) -> Optional[date]:
        """
        Extracts bib creation date
        """
        created_date = sierra_str2date(self["907"]["c"])
        return created_date

    def dewey(self) -> Optional[str]:
        """
        Returns LC suggested Dewey classification then other agency's number.
        Does not alter the class mark string.
        """
        fields = self.get_fields("082")

        # check if LC full ed. present first
        for field in fields:
            if field.indicators == ["0", "0"]:
                class_mark = field["a"].strip()
                class_mark = normalize_dewey(class_mark)
                return class_mark  # type: ignore

        # then other agency full ed.
        for field in fields:
            if field.indicators == ["0", "4"]:
                class_mark = field["a"].strip()
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
                return self["008"].data[23]  # type: ignore
            elif rec_type in "efgk":
                return self["008"].data[29]  # type: ignore
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
            languages.append(self["008"].data[35:38])
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
            return self["010"]["a"].strip()  # type: ignore
        except (AttributeError, TypeError):
            return None

    def main_entry(self) -> Field:
        """
        Returns main entry field instance
        """
        entry_fields = ["100", "110", "111", "245"]
        for field in entry_fields:
            if bool(self[field]):
                return self[field]

    def orders(self, sort: str = "descending") -> List[Order]:
        """
        Parses 960 and 961 as pairs to exctact fixed and variable fields order data

        Args:
            sort:                   'descending' (default, from most recent to oldest) or
                                    'ascending' (from oldest to the newest). Relies no order
                                    of fields in MARC record to make this determination.
        """

        if not isinstance(sort, str) or sort not in "ascending,descending":
            raise BookopsMarcError("Invalid 'sort' argument was passed.")

        orders = []

        for field in self:
            if field.tag == "960":
                f960 = field

                # 961 tag (order variable fields) makes only sense if it is
                # preceeded by 960 tag (order fixed fields); ignore if 960 not
                # present, in the 'pur/pout' export table 960/961 combinations are
                # grouped together
                try:
                    following_field = self.fields[self.pos]
                    if following_field.tag == "961":
                        f961 = following_field
                except IndexError:
                    f961 = None

                order = Order(self.library, f960, f961)
                orders.append(order)

        if sort == "descending":
            orders.reverse()

        return orders

    def overdrive_number(self) -> Optional[str]:
        """
        Returns Overdrive Reserve ID parsed from the 037 tag.
        """
        try:
            return self["037"]["a"].strip()  # type: ignore
        except (AttributeError, TypeError):
            return None

    def remove_unsupported_subjects(self) -> None:
        """
        Deletes subject fields from the record that contain
        unsupported by BPL or NYPL thesauri
        """
        subjects = self.subjects()

        for field in subjects:
            if field.tag not in SUPPORTED_SUBJECT_TAGS:
                self.remove_field(field)
                continue
            if field.indicator2 == "0":  # LCSH
                continue
            if field.indicator2 == "7":
                if "2" in field:
                    if field["2"].strip() in SUPPORTED_THESAURI:
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
        except IndexError:
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
            return self["998"]["d"].strip()
        except (TypeError, AttributeError):
            return None

    def sierra_bib_id(self) -> Optional[str]:
        """
        Retrieves Sierra bib # from the 907 MARC tag
        """
        try:
            bib_id = self["907"]["a"][1:]
        except TypeError:
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
        for field in self.subjects():
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
            code = self["998"]["e"]
        except TypeError:
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
        tag = self["024"]
        if tag:
            if tag.indicator1 == "1":
                try:
                    return tag["a"].strip()  # type: ignore
                except AttributeError:
                    pass
        return None


def pymarc_record_to_local_bib(record: Record, library: str) -> Bib:
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
