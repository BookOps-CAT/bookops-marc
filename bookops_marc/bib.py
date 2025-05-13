# -*- coding: utf-8 -*-

"""
Module replaces pymarc's Record module. Inherits all Record class functionality and
adds some syntactic sugar.
"""

from datetime import date
from itertools import chain
from typing import Dict, List, Optional, Sequence

from pymarc import Field, Indicators, Record
from pymarc.constants import LEADER_LEN

from .constants import SUPPORTED_SUBJECT_TAGS, SUPPORTED_THESAURI
from .errors import BookopsMarcError
from .item import Item
from .local_values import normalize_date
from .models import OclcNumber, Order


class Bib(Record):
    """A class for representing local MARC record."""

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
        # Overriding the type of pymarc.Record.leader
        self.leader: str
        self.library = library.lower()

    def __iter__(self):
        self.pos = 0
        return self

    def __next__(self):
        if self.pos >= len(self.fields):
            raise StopIteration
        self.pos += 1
        return self.fields[self.pos - 1]

    @property
    def audience(self) -> Optional[str]:
        """Retrieves audience code from the 008 MARC tag"""
        field_008 = self.get("008")
        if (
            field_008
            and field_008.data
            and self.leader[6] in "acdgijkmt"
            and self.leader[7] in "am"
        ):
            return field_008.data[22]
        else:
            return None

    @property
    def barcodes(self) -> List[str]:
        """Retrieves barcodes from a record's associated `Item` records"""
        return [i.barcode for i in self.items if self.items and i.barcode]

    @property
    def branch_call_no(self) -> Optional[str]:
        """
        Retrieves branch library call number as string without any MARC coding
        """
        field = self.branch_call_no_field
        if field:
            return field.value()
        else:
            return None

    @property
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

    @property
    def cataloging_date(self) -> Optional[date]:
        """Extracts cataloging date from the bib"""
        cat_date = self.get("907")
        if cat_date and "b" in cat_date:
            return normalize_date(cat_date.get("b"))
        else:
            return None

    @property
    def collection(self) -> Optional[str]:
        """
        Returns the collection that the record is a part of.

        Options are "RL" (for research materials), "BL" (for branch materials),
        "mixed", or None. An NYPL record will have the collection "RL" or "BL" if the
        record contains one 910$a field with the value "RL" or "BL". If an NYPL record
        contains two 910$a fields and both "BL" and "RL", the record's collection will
        be "mixed". All other records will be assigned `None` as the collection type.
        """
        if not self.library == "nypl":
            return None
        subfields = [i.get("a").strip() for i in self.get_fields("910") if i]
        if len(subfields) == 1 and subfields[0] in ["BL", "RL"]:
            return str(subfields[0])
        elif sorted(subfields) == ["BL", "RL"]:
            return "mixed"
        else:
            return None

    @property
    def control_number(self) -> Optional[str]:
        """
        Returns a control number from the 001 tag if it exists.
        """
        field = self.get("001")
        if field and field.data:
            return field.data.strip()
        else:
            return None

    @property
    def created_date(self) -> Optional[date]:
        """Extracts bib creation date"""
        create_date = self.get("907")
        if create_date and "c" in create_date:
            return normalize_date(create_date.get("c"))
        else:
            return None

    @property
    def dewey(self) -> Optional[str]:
        """
        Returns Dewey classification from bib. First checks for LC assigned
        Dewey classification and before checking for Dewey assigned by other
        agencies. Does not alter the class mark string.
        """
        fields = self.get_fields("082")
        class_mark = None
        # check if LC full ed. present first
        lc_class = [i for i in fields if i.indicators == Indicators("0", "0")]
        # then other agency full ed.
        other_agency = [i for i in fields if i.indicators == Indicators("0", "4")]
        if len(lc_class) > 0:
            class_mark = lc_class[0].get("a")
        elif len(lc_class) == 0 and len(other_agency) > 0:
            class_mark = other_agency[0].get("a")
        if not isinstance(class_mark, str):
            return None
        class_mark = (
            class_mark.strip()
            .replace("/", "")
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

    @property
    def dewey_shortened(self) -> Optional[str]:
        """
        Returns Dewey classification shortened to a maximum of 4 digits
        after period. Length of shortened class mark is determined based
        on the bib's library and audience.
            BPL materials: 4 digits (eg. 505.4167)
            NYPL adult/young adult: 4 digits (eg. 505.4167)
            NYPL juvenile materials: 2 digits (eg. 505.41)
        """
        class_mark = self.dewey
        audns = list(chain(*[i.audn for i in self.orders]))
        if not isinstance(class_mark, str):
            return None
        if self.library == "nypl" and all(i == "j" for i in audns):
            digits = 2
        else:
            digits = 4
        class_mark = class_mark[: 4 + digits]
        while len(class_mark) > 3 and class_mark[-1] in ".0":
            class_mark = class_mark[:-1]
        return class_mark

    @property
    def form_of_item(self) -> Optional[str]:
        """
        Returns form of item code from the 008 tag position 23 if
        applicable for a given material format
        """
        rec_type = self.record_type
        field_008 = self.get("008")
        if field_008 and field_008.data and isinstance(rec_type, str):
            if rec_type in "acdijmopt":
                return field_008.data[23]
            elif rec_type in "efgk":
                return field_008.data[29]
        return None

    @property
    def item_fields(self) -> List[Field]:
        """
        Returns a list of fields from which to create `Item` records
        """
        fields = []

        for field in self:
            if field.tag == "949" and field.indicators == Indicators(" ", "1"):
                fields.append(field)
            elif (
                field.tag == "960"
                and self.library == "bpl"
                and self.overdrive_number is None
            ):
                fields.append(field)
        return fields

    @property
    def items(self) -> List[Item]:
        """
        Returns a list of items attached to bib
        """
        return [Item(i) for i in self.item_fields]

    @property
    def languages(self) -> List[str]:
        """
        Returns list of material main languages
        """
        languages = []
        field_008 = self.get("008")
        if field_008 and field_008.data:
            languages.append(field_008.data[35:38])

        for field in self.get_fields("041"):
            for sub in field.get_subfields("a"):
                languages.append(sub)
        return languages

    @property
    def lccn(self) -> Optional[str]:
        """
        Returns Library of Congress Control Number
        """
        field = self.get("010")
        if not field:
            return None
        lccn = field.get("a")
        if isinstance(lccn, str):
            return lccn.strip()
        else:
            return None

    @property
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

    @property
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
        ) -> Optional[OclcNumber]:
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

    @property
    def orders(self) -> Sequence[Order]:
        """
        Returns a list of orders attached to bib. Order data coded in the 960 tag
        (order fixed fields) may be followed by a related 961 tag (order variable
        fields) so iterating over the entire bib is needed to connect the two
        fields. It is possible that the 960 tag may not have a related 961 (BPL).
        """
        orders = []

        for field in self:
            if field.tag == "960":
                try:
                    following_field = self.fields[self.pos]
                except IndexError:
                    following_field = None
                if self.library == "bpl" and field in self.item_fields:
                    continue
                else:
                    orders.append(Order(field, following_field))
        return orders

    @property
    def overdrive_number(self) -> Optional[str]:
        """
        Returns Overdrive Reserve ID parsed from the 037 tag.
        """
        field = self.get("037")
        if not field:
            return None
        overdrive_number = field.get("a")
        if isinstance(overdrive_number, str) and field.get("b") == "OverDrive, Inc.":
            return overdrive_number.strip()
        else:
            return None

    @property
    def physical_description(self) -> Optional[str]:
        """
        Returns value of the first 300 MARC tag in the bib
        """
        try:
            return self.physicaldescription[0].value()
        except (TypeError, IndexError):
            return None

    @property
    def record_type(self) -> Optional[str]:
        """
        Retrieves record type code from MARC leader
        """
        return self.leader[6]

    @property
    def research_call_no(self) -> List[str]:
        """
        Retrieves research library call number as string without any MARC coding
        """
        return [i.value() for i in self.research_call_no_field if i]

    @property
    def research_call_no_field(self) -> List[Field]:
        """
        Retrieves a research library call number field as pymarc.Field instance
        """
        fields = []
        if self.library == "nypl":
            fields.extend(self.get_fields("852"))
        return fields

    @property
    def sierra_bib_format(self) -> Optional[str]:
        """
        Returns Sierra bib format fixed field code
        """
        field = self.get("998")
        if not field:
            return None
        bib_format = field.get("d")
        if isinstance(bib_format, str):
            return bib_format.strip()
        else:
            return None

    @property
    def sierra_bib_id(self) -> Optional[str]:
        """
        Retrieves Sierra bib # from the 907 MARC tag
        """
        field = self.get("907")
        if not field:
            return None
        bib_id = field.get("a")
        if isinstance(bib_id, str) and len(bib_id) > 0:
            return bib_id[1:]
        else:
            return None

    @property
    def sierra_bib_id_normalized(self) -> Optional[int]:
        """
        Retrieves Sierra bib # from the 907 tag and returns it
        without 'b' prefix and the check digit.
        """
        bib_id = self.sierra_bib_id
        if isinstance(bib_id, str):
            return int(bib_id[1:-1])
        else:
            return None

    @property
    def subjects_lc(self) -> List[Field]:
        """
        Retrieves Library of Congress Subject Headings from the bib
        """
        lc_subjects = []
        for field in self.subjects:
            if field.indicator2 == "0":
                lc_subjects.append(field)
        return lc_subjects

    @property
    def suppressed(self) -> bool:
        """
        Determines based on 998 $e value if bib is suppressed from public display
        BPL usage: "c", "n"
        NYPL usage: "c", "e", "n", "q", "o", "v"
        """
        field = self.get("998")
        if not field:
            return False
        code = field.get("e")
        if isinstance(code, str) and code in ("c", "e", "n", "q", "o", "v"):
            return True
        else:
            return False

    @property
    def upc_number(self) -> Optional[str]:
        """
        Returns a UPC number if present on the bib.
        https://www.loc.gov/marc/bibliographic/bd024.html
        """
        tag = self.get("024")
        if tag and tag.indicator1 and tag.indicator1 == "1":
            upc_num = tag.get(code="a")
            if isinstance(upc_num, str):
                return upc_num.strip()
        return None

    def sort_orders(self, sort: str = "descending") -> Sequence[Order]:
        """
        Returns a sorted list of orders attached to a bib. MARC records exported from
        Sierra have orders sorted from oldest to newest (ie. the first 960 tag in a
        record is the oldest order and teh last 960 tag is the newest order).
        Args:
            sort:
                How to sort a record's orders:
                 - ascending (from oldest to most recent), or
                 - descending (from most recent to oldest)
        """
        if not isinstance(sort, str) or sort not in "ascending,descending":
            raise BookopsMarcError("Invalid 'sort' argument was passed.")

        sorted_orders = [i for i in self.orders]

        if sort == "descending":
            sorted_orders.reverse()
        return sorted_orders

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
        controlNo = self.control_number
        if not controlNo or not OclcNumber.is_valid(controlNo):
            pass
        elif self.library == "bpl":
            self["001"].data = OclcNumber(controlNo).with_prefix
        elif OclcNumber.is_valid(controlNo) and self.library == "nypl":
            self["001"].data = OclcNumber(controlNo).without_prefix

    def remove_unsupported_subjects(self) -> None:
        """
        Deletes subject fields from the record that contain
        thesauri unsupported by BPL or NYPL
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

    @classmethod
    def pymarc_record_to_local_bib(cls, record: Record, library: str) -> "Bib":
        """
        Returns an instance of `pymarc.Record` as a `Bib` object

        Args:
            record:
                `pymarc.Record` instance
            library:
                'bpl' or 'nypl'

        Returns:
            `bookops_marc.bib.Bib` instance
        """
        if not isinstance(record, Record):
            raise TypeError(
                "Invalid 'record' argument was passed. Must be a pymarc.Record object."
            )
        else:
            bib = Bib()
            bib.leader = record.leader
            bib.fields = record.fields
            bib.library = library
            return bib
