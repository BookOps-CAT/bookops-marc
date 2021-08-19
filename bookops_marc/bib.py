"""
Module replaces pymarc's Record module. Inherits all Record class functinality and
adds some syntactic sugar.
"""
from typing import Optional

from pymarc import Record
from pymarc.constants import LEADER_LEN


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
