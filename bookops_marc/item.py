# -*- coding: utf-8 -*-

"""
Data models used by bookops-marc.

This module contains the following classes:

`Item`:
    a class that defines a valid `Item` record created from a MARC field
"""

from typing import Optional

from pymarc import Field


class Item:
    """
    A class to represent an `Item` record from a field.

    Attributes:
        barcode:
            the item's barcode from subfield 'i'
        call_no:
            the item's call number from subfield 'a'
        copies:
            the number of copies from subfield 'g'
        initials:
            the initials or vendor code for the item's creator
            from subfield 'v'
        internal_note:
            a free text field from subfield 'n'
        item_agency:
            the item's agency code from subfield 'h'
        item_code_1:
            a fixed field from item code 1 and subfield 'q'
        item_code_2:
            a fixed field from item code 2 and subfield 'r'
        item_id:
            the id for the item record as a string from subfield 'y'.
            removes the "." prefix.
        item_id_normalized:
            the id for the item record as an integer. removes the ".i"
            prefix and check digit before converting the id to an integer.
        item_message:
            a fixed field message from subfield 'u'
        item_status:
            the item's status from subfield 's'
        item_type:
            the item type from subfield 't'
        location:
            the item's location code from subfield 'l'
        message:
            a free text message field from subfield 'm'
        opac_message:
            the record's opac message from subfield 'o'
        price:
            the price of the item from subfield 'p'
        volume:
            the item's volume number from subfield 'c'
    """

    def __init__(self, field: Field) -> None:
        """
        An `Item` object is instantiated from a `pymarc.Field` object. This
        field is a non-public attribute for the class and all other attributes
        are computed from this field.

        Args:
            field:
                an instance of `pymarc.Field`
        """
        self._field = field

    @property
    def barcode(self) -> Optional[str]:
        subfield = self._field.get(code="i")
        if subfield:
            return str(subfield)
        else:
            return None

    @property
    def call_no(self) -> Optional[str]:
        subfield = self._field.get(code="a")
        if subfield:
            return str(subfield)
        else:
            return None

    @property
    def copies(self) -> Optional[str]:
        subfield = self._field.get(code="g")
        if subfield:
            return str(subfield)
        else:
            return None

    @property
    def initials(self) -> Optional[str]:
        subfield = self._field.get(code="v")
        if subfield:
            return str(subfield)
        else:
            return None

    @property
    def internal_note(self) -> Optional[str]:
        subfield = self._field.get(code="n")
        if subfield:
            return str(subfield)
        else:
            return None

    @property
    def item_agency(self) -> Optional[str]:
        subfield = self._field.get("h")
        if subfield:
            return str(subfield)
        else:
            return None

    @property
    def item_code_1(self) -> Optional[str]:
        subfield = self._field.get("q")
        if subfield:
            return str(subfield)
        else:
            return None

    @property
    def item_code_2(self) -> Optional[str]:
        subfield = self._field.get("r")
        if subfield:
            return str(subfield)
        else:
            return None

    @property
    def item_id(self) -> Optional[str]:
        subfield = self._field.get("y")
        if isinstance(subfield, str) and len(subfield) > 1:
            return subfield[1:]
        else:
            return None

    @property
    def item_id_normalized(self) -> Optional[int]:
        item_id = self.item_id
        if isinstance(item_id, str) and item_id[1:].isnumeric():
            return int(item_id[1:-1])
        else:
            return None

    @property
    def item_message(self) -> Optional[str]:
        subfield = self._field.get("u")
        if subfield:
            return str(subfield)
        else:
            return None

    @property
    def item_status(self) -> Optional[str]:
        subfield = self._field.get("s")
        if subfield:
            return str(subfield)
        else:
            return None

    @property
    def item_type(self) -> Optional[str]:
        subfield = self._field.get("t")
        if subfield:
            return str(subfield)
        else:
            return None

    @property
    def location(self) -> Optional[str]:
        subfield = self._field.get(code="l")
        if subfield:
            return str(subfield)
        else:
            return None

    @property
    def message(self) -> Optional[str]:
        subfield = self._field.get("m")
        if subfield:
            return str(subfield)
        else:
            return None

    @property
    def opac_message(self) -> Optional[str]:
        subfield = self._field.get("o")
        if subfield:
            return str(subfield)
        else:
            return None

    @property
    def price(self) -> Optional[str]:
        subfield = self._field.get(code="p")
        if subfield:
            return str(subfield)
        else:
            return None

    @property
    def volume(self) -> Optional[str]:
        subfield = self._field.get("c")
        if subfield:
            return str(subfield)
        else:
            return None
