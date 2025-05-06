# -*- coding: utf-8 -*-

"""
Data models used by bookops-marc.

This module contains the following classes:

`Item`:
    a class that defines a valid `Item` record created from a MARC field
`OclcNumber`:
    a class that defines a valid OCLC number and provides additional properties to add
    or remove its prefix
`Order`:
    a class that defines a `Order` record created from a 960 field and, if available,
    a 961 field.
"""

from datetime import date
from typing import List, Optional, Union

from pymarc import Field

from .local_values import normalize_date


class Item:
    """
    A class to represent an `Item` record from a field.

    Attributes:
        barcode:
            the item's barcode from subfield 'i'
        call_no:
            the item's call number from subfield 'a'
        item_agency:
            the item's agency code from subfield 'h'
        item_message:
            a free text message field from subfield 'u'
        location:
            the item's location code from subfield 'l'
        message:
            a free text message field from subfield 'm'
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
    def item_agency(self) -> Optional[str]:
        subfield = self._field.get("h")
        if subfield:
            return str(subfield)
        else:
            return None

    @property
    def item_id(self) -> Optional[int]:
        subfield = self._field.get("y")
        if not subfield or str(subfield).isalpha():
            return None
        else:
            return int(subfield[2:-1])

    @property
    def item_message(self) -> Optional[str]:
        subfield = self._field.get("u")
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


class OclcNumber:
    def __init__(self, value: str):
        self.value = value

    @property
    def value(self) -> str:
        return self._value

    @value.setter
    def value(self, value: Union[str, int, None]) -> None:
        if isinstance(value, str) and value.lower().startswith("(ocolc)"):
            self._value = value
        else:
            self._value = str(value).lower().strip()
        if not self.is_valid(self.value):
            raise ValueError("Invalid OCLC Number.")

    @property
    def has_prefix(self) -> bool:
        oclc_lower = self.value.lower()
        if (
            oclc_lower.startswith("ocm")
            or oclc_lower.startswith("ocn")
            or oclc_lower.startswith("on")
            or oclc_lower.startswith("(ocolc)")
        ):
            return True
        else:
            return False

    @property
    def with_prefix(self) -> str:
        if self.has_prefix is True and not self.value.lower().startswith("(ocolc)"):
            return self.value
        else:
            num = str(int(self.value.lower().strip("()oclnm")))
            value_length = len(num)
            if value_length <= 8 and value_length >= 1:
                return f"ocm{str(int(num)).zfill(8)}"
            elif value_length == 9:
                return f"ocn{str(int(num))}"
            else:
                return f"on{str(int(num))}"

    @property
    def without_prefix(self) -> str:
        if not self.has_prefix:
            return self.value
        else:
            return str(int(self.value.lower().strip("()oclnm")))

    @staticmethod
    def is_valid(value: Union[str, int, None]) -> bool:
        """
        Determines if given value looks like a legitimate OCLC number.

        Args:
            value:
                identifier as `str`, `int`, or None

        Returns:
            bool
        """
        str_value = str(value).lower()
        num_value = str_value.strip("oclmn()")
        if not value:
            return False
        elif not isinstance(value, str) and not isinstance(value, int):
            return False
        elif str_value.isnumeric() is True and int(value) > 0:
            return True
        elif (
            num_value.isnumeric()
            and (str_value.startswith("ocm") and len(num_value) == 8)
            or (str_value.startswith("ocn") and len(num_value) == 9)
            or (str_value.startswith("on") and len(num_value) >= 10)
            or (str_value.startswith("(ocolc)"))
        ):
            return True
        else:
            return False


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
        branches = [i[:2] for i in self.locs if len(i) >= 2]
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
                loc = f"{sub[:s]}{sub[e + 1 :]}"
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
