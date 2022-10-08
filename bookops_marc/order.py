from datetime import datetime, date
from typing import Generator, List, Optional, Set, Tuple, Union

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
    """
    Normalizes PO per Line (vendor note).
    BPL uses semi-colon, NYPL comma in vendor notes.

    Args:
        ven_note:                   value of vendor note variable field

    Returns:
        normalized note
    """
    if isinstance(ven_note, str):
        ven_note = (
            ven_note.lower()
            .replace("deck", "")
            .replace("sr", "")
            .replace("mm", "")
            .replace("ref", "")
            # .replace("st", "")  # BPL story collection
        )
        ven_note = ven_note.replace(";", ",")
        ven_note_lst = [n.strip().lower() for n in ven_note.split(",")]
        ven_note_lst = [n for n in ven_note_lst if n != "n" and n != "e"]
        ven_note_lst = [n for n in ven_note_lst if n]

        if ven_note_lst:
            return ",".join(ven_note_lst)
        else:
            return None
    else:
        return None


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
        Sierra's not coded values are represented as None type.

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
        self.language = None
        self.locations = ()
        self.orderType = None
        self.price = None
        self.shelf_audn_codes = ()
        self.shelves = ()
        self.status = None
        self.vendorCode = None

        # variable fields
        self.blanketPo = None
        self.isbn = None
        self.internalNote = None
        self.vendorNotes = ()
        self.vendorTitleNo = None

        self._parse_order_fields()

    def _get_blanket_po(self) -> Optional[str]:
        """Returns first blanketPO value from order variable field"""
        return self._get_first_variable_field("m")

    def _get_code1(self) -> Optional[str]:
        """Returns order Code1 from order fixed fields."""
        code = self._get_first_fixed_field("c")
        if code == "-":
            return None
        else:
            return code

    def _get_code2(self) -> Optional[str]:
        """Returns order Code2 from order fixed fields."""
        code = self._get_first_fixed_field("d")
        if code == "-":
            return None
        else:
            return code

    def _get_code3(self) -> Optional[str]:
        """Returns order Code3 from order fixed fields."""
        code = self._get_first_fixed_field("e")
        if code == "-":
            return None
        else:
            return code

    def _get_code4(self) -> Optional[str]:
        """Returns order Code4 from order fixed fields."""
        code = self._get_first_fixed_field("f")
        if code == "-":
            return None
        else:
            return code

    def _get_copies(self) -> Optional[int]:
        """Returns number of copies from order fixed fields."""
        copies = self._get_first_fixed_field("o")
        try:
            return int(copies)
        except ValueError:
            return None

    def _get_country(self) -> Optional[str]:
        """Returns three letter country code from order fixed fields."""
        return self._get_first_fixed_field("x")

    def _get_created_date(self) -> date:
        """Returns order created date serialized as datetime.date object."""
        value = self._get_first_fixed_field("q")
        return datetime.strptime(value, "%d-%m-%y").date()

    def _get_first_fixed_field(self, subfield: str) -> Optional[str]:
        try:
            return self._fixed_field[subfield].strip()
        except AttributeError:
            return None

    def _get_first_variable_field(self, subfield: str) -> Optional[str]:
        try:
            return self._variable_field[subfield].strip()
        except AttributeError:
            return None

    def _get_format(self) -> Optional[str]:
        """Returns material format code from order fixed fields."""
        code = self._get_first_fixed_field("g")
        if code == "-":
            return None
        else:
            return code

    def _get_funds(self) -> Tuple[Optional[str]]:
        """
        Returns as a tuple fund codes encoded in order fixed field.
        """
        funds = []

        for sub in self._fixed_field.get_subfields("u"):
            funds.append(sub)

        return tuple(funds)

    def _get_isbn(self) -> Optional[str]:
        """Returns ISBN from order variable fields."""
        return self._get_first_variable_field("l")

    def _get_language_code(self) -> Optional[str]:
        """Returns a language code from order fixed fields."""
        code = self._get_first_fixed_field("w")
        if not code.strip():
            return None
        else:
            return code

    def _get_locations(self) -> Tuple[str]:
        """
        Returns isolated from location codes branches as a list

        Returns:
            branch codes as a sorted set
        """
        locations = []

        for sub in self._fixed_field.get_subfields("t"):

            # remove any qty data
            loc_code = normalize_location_code(sub)

            branch = get_branch_code(loc_code)
            locations.append(branch)

        return tuple(locations)

    def _get_order_type(self) -> Optional[str]:
        """Returns order type code from order fixed fields."""
        code = self._get_first_fixed_field("i")
        if code == "-":
            return None
        else:
            return code

    def _get_price(self) -> Optional[float]:
        """Returns order price from order fixed fields."""
        value = self._get_first_fixed_field("s")
        try:
            pos = value.rindex("}")
        except ValueError:
            pos = -1

        value = value[pos + 1 :]
        try:
            return float(value)
        except ValueError:
            return None

    def _get_shelf_audience_codes(self) -> Tuple[Optional[str]]:
        """
        Returns list of audience codes extracted from location codes
        """
        audns = []

        for sub in self._fixed_field.get_subfields("t"):
            loc_code = normalize_location_code(sub)

            audn = get_shelf_audience_code(loc_code)
            audns.append(audn)

        return tuple(audns)

    def _get_shelves(self) -> Tuple[Optional[str]]:
        """
        Returns list of shelf codes extracted from location codes
        """
        shelves = []

        for sub in self._fixed_field.get_subfields("t"):
            # remove any qty data
            loc_code = normalize_location_code(sub)

            shelf = get_shelf_code(loc_code)
            shelves.append(shelf)

        return tuple(shelves)

    def _get_status(self) -> Optional[str]:
        """Returns order status from order fixed fields."""
        return self._get_first_fixed_field("m")

    def _get_vendor_code(self) -> str:
        """Returns vendor code from order fixed fields."""
        # not sure how the value looks like for empty code
        # is possible vendor code cannot be empty?
        # verify
        return self._get_first_fixed_field("v")

    def _get_vendor_note(self) -> Optional[str]:
        """
        Returns vendor note (PO per line) encoded in variable field of the order tag
        """
        sub = self._get_first_variable_field("h")
        vendor_note = normalize_vendor_note(sub)
        return vendor_note

    def _parse_order_fields(self):
        # fixed fields
        self.oid = normalize_order_number(self._fixed_field["z"])
        self.code1 = self._get_code1()
        self.code2 = self._get_code2()
        self.code3 = self._get_code3()
        self.code4 = self._get_code4()
        self.copies = self._get_copies()
        self.country = self._get_country()
        self.created = self._get_created_date()
        self.format = self._get_format()
        self.funds = self._get_funds()
        self.language = self._get_language_code()
        self.locations = self._get_locations()
        self.orderType = self._get_order_type()
        self.price = self._get_price()
        self.shelf_audn_codes = self._get_shelf_audience_codes()
        self.shelves = self._get_shelves()
        self.status = self._get_status()
        self.vendorCode = self._get_vendor_code()

        # variable fields
        if self._variable_field is not None:
            self.vendorNote = self._get_vendor_note()
            self.blanketPo = self._get_blanket_po()
            self.isbn = self._get_isbn()

    def unique_funds(self) -> Set[str]:
        return set(self.funds)

    def unique_locations(self) -> Set[str]:
        return set(self.locations)

    def unique_shelf_audn_codes(self) -> Set[str]:
        return set(self.shelf_audn_codes)

    def unique_shelves(self) -> Set[str]:
        return set(self.shelves)
