from typing import Generator, Optional, Union

from pymarc import Record, Field

from bookops_marc.bib import Bib
from bookops_marc.models import Order


class Order:
    def __init__(self, library: str, f960: Field, f961: Optional[Field]) -> None:
        """
        Instates Order object
        """

        self.f960 = f960
        self.f961 = f961
        self.audn = None

        # fixed fields
        self.code1 = None
        self.code2 = None
        self.code3 = None
        self.code4 = None
        self.copies = None
        self.country = None
        self.created = None
        self.format = None
        self.funds = ()
        self.locations = ()
        self.lang = None
        self.orderType = None
        self.price = None
        self.status = None
        self.venCode = None

        # variable fields
        self.blanketPo = None
        self.orderIsbn = None
        self.internalNote = None
        self.vendorNotes = ()
        self.vendorTitleNo = None

        self._parse_order_fields()

    def _parse_order_fields(self):
        pass

    def unique_branches(self):
        pass

    def unique_shelves(self):
        pass

    def unique_shelves_audn(self):
        pass

    def unique_funds(self):
        pass
