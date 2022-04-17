# -*- coding: utf-8 -*-

"""
Data models used by bookops-marc
"""
from collections import namedtuple


Order = namedtuple(
    "Order",
    [
        "oid",
        "audn",
        "branches",
        "copies",
        "created",
        "form",
        "lang",
        "shelves",
        "status",
        "venNotes",
    ],
    defaults=[None, None, None, None, None, None, None, None, None],
)
