"""
Module replaces pymarc's Record module. Inherits all Record class functinality and
adds some syntactic sugar.
"""
from typing import Optional

from pymarc import Record, Field
from pymarc.constants import LEADER_LEN


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
