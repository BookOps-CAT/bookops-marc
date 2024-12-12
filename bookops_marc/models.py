# -*- coding: utf-8 -*-

"""
Data models used by bookops-marc
"""

from datetime import date
from typing import List, Optional
from pymarc import Field
from .local_values import normalize_date


class Order:
    """
    A class to represent an `Order` record from a pair of MARC fields.
    Attributes are computed from a MARC 960 field and the following field
    its tag is 961.

    Attributes:
        audn:
            a list of audience codes from the third character of the
            location code
        branches:
            a list of branch codes from the first two characters of the
            location code
        copies:
            an integer representing the number of copies on an order
            from subfield 'o'.
        created:
            the date the order was created as a datetime.date object
            from subfield 'q'
        form:
            the format of the materials being ordered from subfield 'g'.
        lang:
            the language of the materials being ordered from subfield 'w'.
        locs:
            a list of location codes from subfield 't'
        oid:
            the normalized order id as an integer from subfield 'z'
        shelves:
            a list of shelf locations from the fourth and fifth characters
            of the location code
        status:
            the order's status from subfield 'm'
        venNotes:
            if the record's 960 field is followed by a 961 field, the vendor
            notes as a string from subfield 'h' of the 961 field
    """

    def __init__(self, field: Field, following_field: Optional[Field]) -> None:
        """
        An `Order` object is instantiated from 1-2 `pymarc.Field` objects. These
        fields are non-public attributes for the class and all other attributes
        are computed from these fields.

        Args:
            field:
                an instance of `pymarc.Field`
            following_field:
                either an instance of `pymarc.Field` or `None`. This is the
                field that follows the 960 field used to instantiate an `Order`
                object. If the 960 field was the last field in the record
                then following_field is None.
        """
        self._field = field
        self._following_field = following_field

    @property
    def audn(self) -> List[str]:
        audns = [i[2].strip() for i in self.locs if len(i) >= 3]
        return [i for i in audns if i]

    @property
    def branches(self) -> List[str]:
        branches = [i[:2] for i in self.locs if len(i) >= 3]
        return [i for i in branches if i]

    @property
    def copies(self) -> Optional[int]:
        subfield = str(self._field.get(code="o"))
        if subfield.isnumeric():
            return int(subfield)
        else:
            return None

    @property
    def created(self) -> Optional[date]:
        return normalize_date(self._field.get(code="q"))

    @property
    def form(self) -> Optional[str]:
        subfield = str(self._field.get(code="g"))
        if subfield and len(subfield) == 1:
            return str(subfield)
        else:
            return None

    @property
    def lang(self) -> Optional[str]:
        subfield = str(self._field.get(code="w"))
        if subfield and len(subfield) == 3:
            return subfield
        else:
            return None

    @property
    def locs(self) -> List[str]:
        locs = []
        for sub in self._field.get_subfields("t"):
            try:
                s = sub.index("(")
                e = sub.index(")")
                loc = f"{sub[:s]}{sub[e + 1:]}"
            except (ValueError, TypeError, AttributeError):
                loc = sub
            if loc:
                locs.append(loc)
        return locs

    @property
    def oid(self) -> Optional[int]:
        order_num = self._field.get(code="z")
        if not order_num or str(order_num).isalpha():
            return None
        else:
            return int(order_num[2:-1])

    @property
    def shelves(self) -> List[str]:
        shelves = [i[3:5].strip() for i in self.locs if len(i) >= 5]
        return [i for i in shelves if i]

    @property
    def status(self) -> Optional[str]:
        subfield = str(self._field.get(code="m"))
        if subfield and len(subfield) == 1:
            return str(subfield)
        else:
            return None

    @property
    def venNotes(self) -> Optional[str]:
        if self._following_field and self._following_field.tag == "961":
            venNotes: Optional[str] = self._following_field.get("h", None)
            return venNotes
        else:
            return None
