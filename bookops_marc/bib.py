# -*- coding: utf-8 -*-

"""
Module replaces pymarc's Record module. Inherits all Record class functinality and
adds some syntactic sugar.
"""
from datetime import datetime, date
from typing import List, Optional, Dict

from pymarc import Record, Field
from pymarc.constants import LEADER_LEN

from .errors import BookopsMarcError
from .models import Order
from .constants import SUPPORTED_THESAURI, SUPPORTED_SUBJECT_TAGS


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


def normalize_date(order_date: str) -> Optional[date]:
    """
    Returns order created date in datetime format
    """
    try:
        if len(order_date) == 8:
            return datetime.strptime(order_date[:8], "%m-%d-%y").date()
        else:
            return datetime.strptime(order_date[:10], "%m-%d-%Y").date()
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
            float(class_mark)
        except ValueError:
            return None
        else:
            while len(class_mark) > 4 and class_mark[-1] == "0":
                class_mark = class_mark[:-1]
            return class_mark
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

    def _get_shelf_audience_codes(self, field: Field) -> List[Optional[str]]:
        """
        Returns list of audience codes extracted from location codes
        """
        audns = []

        for sub in field.get_subfields("t"):
            loc_code = normalize_location_code(sub)

            audn = get_shelf_audience_code(loc_code)
            audns.append(audn)

        return audns

    def _get_shelves(self, field: Field) -> List[Optional[str]]:
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
        cat_date = normalize_date(self.get("907").get(code="b"))
        return cat_date

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
        created_date = normalize_date(self.get("907").get(code="c"))
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
                class_mark = field.get(code="a").strip()
                class_mark = normalize_dewey(class_mark)
                return class_mark  # type: ignore

        # then other agency full ed.
        for field in fields:
            if field.indicators == ["0", "4"]:
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
            languages.append(self.get("008").data[35:38])
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

    def main_entry(self) -> Field:
        """
        Returns main entry field instance
        """
        entry_fields = ["100", "110", "111", "245"]
        for field in entry_fields:
            if bool(self.get(field)):
                return self.get(field)

    def orders(self, sort: str = "descending") -> List[Order]:
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
                oid = normalize_order_number(field.get(code="z"))

                audns = self._get_shelf_audience_codes(field)
                branches = self._get_branches(field)
                copies = int(field.get(code="o"))
                form = field.get(code="g")
                created = normalize_date(field.get(code="q"))
                lang = field.get(code="w")
                shelves = self._get_shelves(field)
                status = field.get(code="m").strip()

                try:
                    venNotes = None
                    following_field = self.fields[self.pos]
                    if following_field.tag == "961":
                        venNotes = following_field.get(code="h")
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
            return self.get("998").get(code="d").strip()
        except (TypeError, AttributeError):
            return None

    def sierra_bib_id(self) -> Optional[str]:
        """
        Retrieves Sierra bib # from the 907 MARC tag
        """
        try:
            bib_id = self.get("907").get(code="a")[1:]
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
            code = self.get("998").get(code="e")
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

    def flat_dict(self) -> Dict[str, str]:
        """
        Turn a Bib into a dict with all fields in key,value pairs
        Avoids the {"leader": value, "fields": []} structure of as_dict() method
        """
        record: Dict = {"leader": str(self.leader)}

        for field in self:
            if field.tag < "010" and field.tag.isdigit():
                record[field.tag] = field.data
            else:
                data = {
                    "ind1": field.indicator1,
                    "ind2": field.indicator2,
                    "subfields": [{s.code: s.value} for s in field.subfields],
                }
                record[field.tag] = data
        return record


def pymarc_record_to_local_bib(record: Record, library: str) -> Bib:
    """
    Converts an instance of `pymarc.Record` to `bookops_marc.Bib`

    Args:
        record:                 `pymarc.Record` instance
        library:                'bpl' or 'nypl'

    Returns:
        `bookops_marc.bib.Bib` instance
    """
    # if isinstance(record, Record):
    bib = Bib(library=library)
    bib.leader = record.leader
    bib.fields = record.fields[:]

    return bib
