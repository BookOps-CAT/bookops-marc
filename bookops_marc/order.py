from typing import Generator, Optional, Union

from pymarc import Record, Field

from bookops_marc.bib import Bib
from bookops_marc.models import Order


class OrderReader:
    def __init__(self, library: str, bib: Union[Bib, Record]) -> None:
        """
        Generator. Parses order records encoded in 960 and 961 fields of MARC record.

        Args:
            library:		'BPL' or 'NYPL'
            bib:			`bookops_marc.bib.Bib` or `pymarc.record.Record` instance
        """
        if not isinstance(library, str) or library.lower() not in ("bpl", "nypl"):
            raise ValueError(
                "Invalid 'library' argument passed. Only 'BPL' or 'NYPL' are permitted."
            )

        if not isinstance(bib, Bib) or not isinstance(bib, Record):
            raise ValueError(
                "Invalid argument 'bib' was passed. "
                "Must be bookops_marc.bib.Bib or pymarc.record.Record instance."
            )

        self.bib = bib

    def __next__(self):
        for field in self.bib:
            if field.tag == "960":
                f960 = field

                # 961 tag (order variable fields) makes only sense if it is
                # preceeded by 960 tag (order fixed fields); ignore if 960 not
                # present, in the 'pur/pout' export table 960/961 combinations are
                # grouped together
                try:
                    following_field = bib.fields[bib.pos]
                    if following_field.tag == "961":
                        f961 = following_field
                except IndexError:
                    f961 = None

                order = Order(library, f960, f961)
                yield order

    def __iter__(self):
        return self


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
        self.venNotes = ()
        self.blanketPo = None
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
