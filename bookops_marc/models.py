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
        self.copies: Optional[int] = int(field.get(code="o", default=0))
        self.created: Optional[date] = normalize_date(field.get(code="q"))
        self.form: Optional[str] = field.get(code="g")
        self.lang: Optional[str] = field.get(code="w")
        self.locs: List[str] = self._get_location_codes(field)
        self.oid: int = self._normalize_order_number(field)
        self.status: Optional[str] = field.get(code="m")
        self.venNotes: Optional[str] = self._get_venNotes(following_field)

    def _get_location_codes(self, field: Field) -> List[str]:
        """Returns location codes from 960$t"""
        locs = []
        for sub in field.get_subfields("t"):
            try:
                s = sub.index("(")
                e = sub.index(")")
                loc = f"{sub[:s]}{sub[e + 1:]}"
            except (ValueError, TypeError, AttributeError):
                loc = sub
            if loc:
                locs.append(loc)
        return locs

    def _get_venNotes(self, following_field: Optional[Field]) -> Optional[str]:
        """
        Returns vendor notes

        Args:
            following_field:
                either an instance of pymarc.Field or None. This should
                field that follows the 960 field used to instantiate an Order
                object. If the 960 field was the last field in the record
                then following_field is None.
        Returns:
            vendor note as a string or None if subfield h does not exist
        """
        if following_field and following_field.tag == "961":
            venNotes: Optional[str] = following_field.get("h", None)
            return venNotes
        else:
            return None

    def _normalize_order_number(self, field: Field) -> int:
        """Normalizes Sierra order number"""
        order_num = field.get(code="z")
        if not order_num:
            raise ValueError("Order field must contain an order number (960$z)")
        return int(order_num[2:-1])

    @property
    def audn(self) -> List[str]:
        audns = []
        for loc in self.locs:
            if len(loc) >= 3:
                audn = loc[2].strip()
            else:
                audn = None
            if audn:
                audns.append(audn)
        return audns

    @property
    def branches(self) -> List[str]:
        branches = []
        for loc in self.locs:
            if len(loc) >= 3:
                branch = loc[:2]
            else:
                branch = None
            if branch:
                branches.append(branch)
        return branches

    @property
    def shelves(self) -> List[str]:
        shelves = []
        for loc in self.locs:
            if len(loc) >= 5:
                shelf = loc[3:5].strip()
            else:
                shelf = None
            if shelf:
                shelves.append(shelf)
        return shelves
