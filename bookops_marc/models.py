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
    A class to represent an Order record
    """

    def __init__(self, field: Field, following_field: Optional[Field]) -> None:
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
