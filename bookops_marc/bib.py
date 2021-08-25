"""
Module replaces pymarc's Record module. Inherits all Record class functinality and
adds some syntactic sugar.
"""
from collections import namedtuple
from datetime import datetime
from typing import List, Optional

from pymarc import Record, Field
from pymarc.constants import LEADER_LEN

from .errors import BookopsMarcError
from .models import Order


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


def get_branch_code(location_code: str) -> str:
    """
    Returns branch code from normalized location code
    """
    branch = location_code[:2]
    return branch


def normalize_date(order_date: str) -> datetime:
    """
    Returns order created date in datetime format
    """
    return datetime.strptime(order_date, "%d-%m-%y")


def get_shelf_audience_code(location_code: str) -> Optional[str]:
    """
    Parses audience code from given normalized location_code
    """
    try:
        return location_code[2]
    except IndexError:
        return None


def normalize_order_number(order_number: str) -> int:
    """
    Normalizes Sierra order number
    """
    return int(order_number[2:-1])


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

        self.library = library

    def sierra_bib_no(self) -> Optional[str]:
        """
        Retrieves Sierra bib # from the 907 MARC tag
        """
        try:
            return self["907"]["a"][1:]
        except TypeError:
            return None

    def sierra_bib_no_normalized(self) -> Optional[str]:
        """
        Retrieves Sierra bib # from the 907 tag and returns it
        without 'b' prefix and the check digit.
        """
        return self.sierra_bib_no()[1:-1]

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

    def record_type(self) -> Optional[str]:
        """
        Retrieves record type code from MARC leader
        """
        return self.leader[6]

    def physical_description(self) -> Optional[str]:
        """
        Returns value of the first 300 MARC tag in the bib
        """
        try:
            return self.physicaldescription()[0].value()
        except IndexError:
            return None

    def main_entry(self) -> Field:
        """
        Returns main entry field instance
        """
        entry_fields = ["100", "110", "111", "245"]
        for field in entry_fields:
            if bool(self[field]):
                return self[field]

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

    def form_of_item(self) -> Optional[str]:
        """
        Returns form of item code from the 008 tag position 23 if applicable for
        a given material format
        """
        rec_type = self.record_type()
        if rec_type in "acdijopt":
            return self["008"].data[23]
        elif rec_type == "g":
            return self["008"].data[29]
        else:
            return None

    def _get_branches(self, field: Field) -> List[str]:
        """
        Returns isolated from location codes branches as a list
        """
        branches = []

        for sub in field.get_subfields("t"):

            # remove any qty data
            loc_code = normalize_location_code(sub)

            branch = get_branch_code(loc_code)
            branches.append(branch)

        return branches

    def orders(
        self, library: str = None, order: str = "descending"
    ) -> List[namedtuple]:
        """
        Returns a list of order attached to bib. To correctly parse order field
        a library must be specified since mapping varies in both systems.

        Args:
            library:                "bpl" or "nypl" (mandatory)
            order:                  ascending (from most recent to oldest) or
                                    descending (from oldest to most recent)
        """
        if library is None:
            raise BookopsMarcError(
                "Must specify 'library' argument. Order field mapping varies between "
                " both systems."
            )
        elif not isinstance(library, str):
            raise BookopsMarcError("'library' argument  must be a string.")
        library = library.lower()
        if library not in "nypl,bpl":
            raise BookopsMarcError(
                "'library' argument have only two permissable values: 'nypl' and 'bpl'."
            )

        orders = []

        for field in self.get_fields("960"):
            # shared mapping
            oid = normalize_order_number(field["z"])
            first_location_code = normalize_location_code(field["t"])
            audn = get_shelf_audience_code(first_location_code)
            status = field["m"].strip()
            branches = self._get_branches(field)
            copies = int(field["o"])
            created = normalize_date(field["q"])

            # variant mapping
            if library == "nypl":
                pass
            elif library == "bpl":
                pass

            o = Order(
                oid,
                audn=audn,
                branches=branches,
                copies=copies,
                created=created,
                form=None,
                lang=None,
                shelves=None,
                status=status,
                venNotes=None,
            )
            orders.append(o)

        return orders
