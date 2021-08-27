"""
Module replaces pymarc's Record module. Inherits all Record class functinality and
adds some syntactic sugar.
"""
from collections import namedtuple
from datetime import datetime, date
from typing import List, Optional

from pymarc import Record, Field
from pymarc.constants import LEADER_LEN

from .errors import BookopsMarcError
from .models import Order


def get_branch_code(location_code: str) -> str:
    """
    Returns branch code from normalized location code
    """
    branch = location_code[:2]
    return branch


def get_shelf_audience_code(location_code: str) -> Optional[str]:
    """
    Parses audience code from given normalized location_code
    """
    try:
        audn = location_code[2].strip()
        if audn:
            return audn
        else:
            return None

    except IndexError:
        return None


def get_shelf_code(location_code: str) -> Optional[str]:
    """
    Parses shelf code from given normalized location_code
    """
    try:
        shelf = location_code[3:5].strip()
        if shelf:
            return shelf
        else:
            return None
    except (TypeError, IndexError):
        return None


def normalize_date(order_date: str) -> datetime:
    """
    Returns order created date in datetime format
    """
    try:
        if len(order_date) == 16:
            return datetime.strptime(order_date[:10], "%m-%d-%Y").date()
        elif len(order_date) == 8:
            return datetime.strptime(order_date[:8], "%m-%d-%y").date()
    except ValueError:
        return None


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
            # test if has correct format
            float(class_mark)
            while class_mark[-1] == "0":
                class_mark = class_mark[:-1]
            return class_mark
        except ValueError:
            return None
    else:
        return None


def normalize_location_code(code: str) -> str:
    """
    Removes any quantity designation from location code value
    """
    try:
        s = code.index("(")
        e = code.index(")")
        return f"{code[:s]}{code[e + 1:]}"
    except ValueError:
        return code


def normalize_order_number(order_number: str) -> int:
    """
    Normalizes Sierra order number
    """
    return int(order_number[2:-1])


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
    This implementation fixes pymarc.Record bug (?) which unable accessing
    current position in the iterator (overwrites pymarc.Record's
    __iter__ and __next__ methods).
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

        self.library = library

    def __iter__(self):
        self.pos = 0
        return self

    def __next__(self):
        if self.pos >= len(self.fields):
            raise StopIteration
        self.pos += 1
        return self.fields[self.pos - 1]

    def _get_branches(self, field: Field) -> List[str]:
        """
        Returns isolated from location codes branches as a list

        Args:
            field:                  pymarc.Field instance
        """
        branches = []

        for sub in field.get_subfields("t"):

            # remove any qty data
            loc_code = normalize_location_code(sub)

            branch = get_branch_code(loc_code)
            branches.append(branch)

        return branches

    def _get_shelf_audience_codes(self, field: Field) -> List[str]:
        """
        Returns list of audience codes extracted from location codes
        """
        audns = []

        for sub in field.get_subfields("t"):
            loc_code = normalize_location_code(sub)

            audn = get_shelf_audience_code(loc_code)
            audns.append(audn)

        return audns

    def _get_shelves(self, field: Field) -> List[str]:
        """
        Returns list of shelf codes extracted from location codes

        Args:
            field:                  pymarc.Field instance
        """
        shelves = []

        for sub in field.get_subfields("t"):
            # remove any qty data
            loc_code = normalize_location_code(sub)

            shelf = get_shelf_code(loc_code)
            shelves.append(shelf)

        return shelves

    def audience(self) -> Optional[str]:
        """
        Retrieves audience code from the 008 MARC tag
        """
        try:
            if self.leader[6] in "acdgijkmt" and self.leader[7] in "am":
                code = self["008"].data[22]
            else:
                code = None
        except AttributeError:
            code = None
        return code

    def branch_call_no(self) -> Optional[str]:
        """
        Retrieves branch library call number as string without any MARC coding
        """
        if self.library == "bpl":
            try:
                return self["099"].value()
            except AttributeError:
                return None
        elif self.library == "nypl":
            try:
                return self["091"].value()
            except AttributeError:
                return None
        else:
            return None

    def cataloging_date(self) -> Optional[date]:
        """
        Extracts cataloging date from the bib
        """
        cat_date = normalize_date(self["907"]["b"])
        return cat_date

    def created_date(self) -> Optional[date]:
        """
        Extracts bib creation date
        """
        created_date = normalize_date(self["907"]["c"])
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
                return class_mark

        # then other agency full ed.
        for field in fields:
            if field.indicators == ["0", "4"]:
                class_mark = field["a"].strip()
                class_mark = normalize_dewey(class_mark)
                return class_mark

    def dewey_normalized(self) -> Optional[str]:
        """
        Returns LC suggested Dewey classification then other agency's number
        if present .
        """
        class_mark = self.dewey()
        class_mark = shorten_dewey(class_mark)
        return class_mark

    def form_of_item(self) -> Optional[str]:
        """
        Returns form of item code from the 008 tag position 23 if applicable for
        a given material format
        """
        rec_type = self.record_type()
        if rec_type in "acdijmopt":
            return self["008"].data[23]
        elif rec_type in "efgk":
            return self["008"].data[29]
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

    def main_entry(self) -> Field:
        """
        Returns main entry field instance
        """
        entry_fields = ["100", "110", "111", "245"]
        for field in entry_fields:
            if bool(self[field]):
                return self[field]

    def orders(self, sort: str = "descending") -> List[namedtuple]:
        """
        Returns a list of order attached to bib

        Args:
            sort:                   ascending (from oldest to most recent) or
                                    descending (from recent to oldest)
        """

        if not isinstance(sort, str) or sort not in "ascending,descending":
            raise BookopsMarcError("Invalid 'sort' argument was passed.")

        orders = []

        # order data coded in the 960 tag (order fixed fields) may be followed by
        # related 961 tag (order variable field) so iterating over entire bib
        # is needed to connect these two;
        # it is possible 960 tag may not have related 961 (BPL)

        for field in self:
            if field.tag == "960":
                # shared NYPL & BPL mapping
                oid = normalize_order_number(field["z"])

                audns = self._get_shelf_audience_codes(field)
                branches = self._get_branches(field)
                copies = int(field["o"])
                form = field["g"]
                created = normalize_date(field["q"])
                lang = field["w"]
                shelves = self._get_shelves(field)
                status = field["m"].strip()

                try:
                    venNotes = None
                    following_field = self.fields[self.pos]
                    if following_field.tag == "961":
                        venNotes = following_field["h"]
                except IndexError:
                    pass

                o = Order(
                    oid,
                    audn=audns,
                    branches=branches,
                    copies=copies,
                    created=created,
                    form=form,
                    lang=lang,
                    shelves=shelves,
                    status=status,
                    venNotes=venNotes,
                )
                orders.append(o)

        if sort == "descending":
            orders.reverse()

        return orders

    def physical_description(self) -> Optional[str]:
        """
        Returns value of the first 300 MARC tag in the bib
        """
        try:
            return self.physicaldescription()[0].value()
        except IndexError:
            return None

    def record_type(self) -> Optional[str]:
        """
        Retrieves record type code from MARC leader
        """
        return self.leader[6]

    def sierra_bib_id(self) -> Optional[str]:
        """
        Retrieves Sierra bib # from the 907 MARC tag
        """
        try:
            return self["907"]["a"][1:]
        except TypeError:
            return None

    def sierra_bib_id_normalized(self) -> Optional[str]:
        """
        Retrieves Sierra bib # from the 907 tag and returns it
        without 'b' prefix and the check digit.
        """
        return self.sierra_bib_id()[1:-1]

    def subjects_lc(self) -> List[Field]:
        """
        Retrieves Library of Congress Subject Headings from the bib
        """
        lc_subjects = []
        for field in self.subjects():
            if field.indicator2 == "0":
                lc_subjects.append(field)
        return lc_subjects
