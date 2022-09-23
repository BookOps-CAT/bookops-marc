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
    def __init__(self, library: str, f960: Field, f961: Optional[Field] = None) -> None:
        """
        Instates Order object
        """

        self._960 = f960
        self._961 = f961
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

    def _parse_order_fields(self):
        self.oid = normalize_order_number(self._960["z"])
        try:
            self.vendorNote = normalize_vendor_note(self._961["h"])
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
