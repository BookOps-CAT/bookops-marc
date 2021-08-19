from bookops_marc import SierraBibReader


def test_SierraBibReader_iteration():
    with open("tests/nyp-sample.mrc", "rb") as marcfile:
        reader = SierraBibReader(marcfile, library="nypl", hide_utf8_warnings=True)
        n = 0
        for bib in reader:
            n += 1
        assert n == 9
