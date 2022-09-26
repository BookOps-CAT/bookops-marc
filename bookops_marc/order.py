from typing import Generator, List, Optional, Union

from pymarc import Record, Field


def get_branch_code(location_code: str) -> str:
    """
    Returns branch code from normalized location code
    """
    branch = location_code[:2]
    return branch


def get_shelf_code(location_code: str) -> Optional[str]:
    """
    Parses shelf code from given normalized location_code
    """
    try:
        shelf = location_code[3:5].strip()
        if shelf:
            return shelf
        else:
            return None
    except (TypeError, IndexError):
        return None


def normalize_location_code(code: str) -> str:
    """
    Removes any quantity designation from location code value
    """
    try:
        s = code.index("(")
        e = code.index(")")
        return f"{code[:s]}{code[e + 1:]}"
    except ValueError:
        return code


def normalize_order_number(order_number: str) -> int:
    """
    Normalizes Sierra order number

    Args:
        order_number:               Sierra full order number including a prefix and digit check

    Returns:
        int
    """
    return int(order_number[2:-1])


def normalize_vendor_note(ven_note: str) -> Optional[str]:
    pass


def get_shelf_audience_code(location_code: str) -> Optional[str]:
    """
    Parses audience code from given normalized location_code
    """
    try:
        audn = location_code[2].strip()
        if audn:
            return audn
        else:
            return None

    except IndexError:
        return None


class Order:
    def __init__(
        self, library: str, fixed_field: Field, variable_field: Optional[Field] = None
    ) -> None:
        """
        Instates Sierra Order object.

        Args:
            library:                'bpl' or 'nypl' code
            fixed_field:            `pymarc.field.Field` instance (960 tag)
            variable_field:         `pymarc.field.Field` instance (961 tag)

        """
        if not isinstance(library, str):
            raise TypeError("Invalid 'library' argument type. Must be a string.")
        else:
            if library.lower() not in ("bpl", "nypl"):
                raise ValueError(
                    "Invalid 'library' argument value. Must be 'BPL' or 'NYPL'"
                )

        if not isinstance(fixed_field, Field):
            raise TypeError(
                "Invalid 'fixed_field' argument. Must be pymarc.field.Field instance."
            )

        if isinstance(variable_field, Field) or variable_field is None:
            pass
        else:
            raise TypeError(
                "Invalid 'variable_field' argument. Must be pymarc.field.Field or None."
            )

        self.library = library.lower()
        self._fixed_field = fixed_field
        self._variable_field = variable_field
        self.audn = None

        # fixed fields
        self.oid = None
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

    def _get_branches(self, field: Field) -> List[str]:
        """
        Returns isolated from location codes branches as a list

        Args:
            field:                  pymarc.Field instance
        """
        branches = []

        for sub in field.get_subfields("t"):

            # remove any qty data
            loc_code = normalize_location_code(sub)

            branch = get_branch_code(loc_code)
            branches.append(branch)

        return branches

    def _get_shelf_audience_codes(self) -> List[Optional[str]]:
        """
        Returns list of audience codes extracted from location codes
        """
        audns = []

        for sub in self._fixed_field.get_subfields("t"):
            loc_code = normalize_location_code(sub)

            audn = get_shelf_audience_code(loc_code)
            audns.append(audn)

        return audns

    def _get_shelves(self) -> List[Optional[str]]:
        """
        Returns list of shelf codes extracted from location codes
        """
        shelves = []

        for sub in self._fixed_field.get_subfields("t"):
            # remove any qty data
            loc_code = normalize_location_code(sub)

            shelf = get_shelf_code(loc_code)
            shelves.append(shelf)

        return shelves

    def _parse_order_fields(self):
        self.oid = normalize_order_number(self._fixed_field["z"])
        try:
            self.vendorNote = normalize_vendor_note(self._variable_field["h"])
        except (TypeError, KeyError):
            pass

    def unique_branches(self):
        pass

    def unique_shelves(self):
        pass

    def unique_shelves_audn(self):
        pass

    def unique_funds(self):
        pass
