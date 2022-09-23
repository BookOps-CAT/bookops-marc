from datetime import datetime, date
from typing import Optional


def sierra_str2date(date_str: str) -> Optional[date]:
    """
    Returns date retrieved from Sierra in datetime format
    BPL & NYPL Sierra follows slightly different pattern, especially
    considering legacy records.

    Args:
        date_str:               Sierra's record value including date
                                or datetime data

    Returns:
        `datetime.date` instance
    """
    try:
        if len(date_str) == 8:
            return datetime.strptime(date_str[:8], "%m-%d-%y").date()
        else:
            return datetime.strptime(date_str[:10], "%m-%d-%Y").date()
    except ValueError:
        return None
