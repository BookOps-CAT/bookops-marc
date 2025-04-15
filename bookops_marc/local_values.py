"""
This module contains helper methods for parsing and manipulating local Sierra fields
"""

from datetime import date, datetime
from typing import Optional


def normalize_date(order_date: str) -> Optional[date]:
    """
    Returns order created date in datetime format
    """
    try:
        if len(order_date) == 8:
            return datetime.strptime(order_date[:8], "%m-%d-%y").date()
        else:
            return datetime.strptime(order_date[:10], "%m-%d-%Y").date()
    except (ValueError, TypeError):
        return None
