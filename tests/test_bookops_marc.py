import pytest

from bookops_marc import __version__


def test_version():
    assert __version__ == "0.12.0"


def test_Bib_top_import():
    try:
        from bookops_marc import Bib  # noqa: F401
    except ImportError:
        pytest.fail("Top level Bib import failed.")


def test_SierraBibReader_top_import():
    try:
        from bookops_marc import SierraBibReader  # noqa: F401
    except ImportError:
        pytest.fail("Top level SierraBibReader failed.")
