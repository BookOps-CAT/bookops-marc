![tests](https://github.com/BookOps-CAT/bookops-marc/actions/workflows/unit-tests.yaml/badge.svg?branch=master) [![Coverage Status](https://coveralls.io/repos/github/BookOps-CAT/bookops-marc/badge.svg?branch=master)](https://coveralls.io/github/BookOps-CAT/bookops-marc?branch=master) [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

# bookops-marc

A sweetened [`pymarc.Record`](https://pymarc.readthedocs.io/en/latest/_modules/pymarc/record.html) module tailored for data extraction from local Sierra's MARC dumps.

## Installation
Install via pip:

```bash
python -m pip install git+https://github.com/BookOps-CAT/bookops-marc
```

## Usage

```python
from bookops_marc import SierraBibReader

with open ('marc.mrc', "rb") as marcfile:
	reader = SierraBibReader(marcfile)
	for bib in reader:
		print(bib.sierra_bib_id_normalized())
		print(bib.branch_call_no())
		print(bib.orders())
		print(bib.main_entry())
		print(bib.form_of_item())
		print(bib.dewey())
		print(bib.dewey_shortened())
```

Python 3.8 and up.

## Version
> 0.7.0

## Changelog
### [0.7.0] - 2022-04-16
#### Added
+ remove_unsupported_subjects() that deletes subject tags (6xx) which are not supported by BookOps (NYPL & BPL CAT)
+ dev dependency mypy 0.942
+ basic type checking

#### Changed
+ pytest bumped to 7.1.1
+ pytest-cov bumped to 3.0.0

### [0.6.1] - 2022-04-13
#### Fixed
+ parsing of NYPL bib created date Sierra field (907$c)

#### Changed
+ bumps pymarc to v4.2.0

### [0.6.0] - 2022-02-06
#### Changed
+ CI moved from Travis to Github-Actions
    + added Python 3.10 tests

### [0.5.0] - 2021-11-15
#### Added
+ `bib.suppressed()` method to `Bib` which determines if bib is suppressed from the public display

### [0.4.0]  - 2021-09-23
#### Added
+ `bib.control_number()` method to `Bib` (retrieves data from the tag 001)

### [0.3.0] - 2021-09-23
#### Added
+ `bib.lccn()` (retrieves LCCN from bib),
+ `bib.overdrive_number()` (retrieves Overdrive Reserve ID),
+ `bib.upc_number()` (retrieves UPC from bib)

### [0.2.0] - [2021-08-30]
#### Added
+ a method for retrieving branch call number as `pymarc.Field`

[0.6.1]: https://github.com/BookOps-CAT/bookops-marc/compare/v0.6.0...v0.6.1
[0.6.0]: https://github.com/BookOps-CAT/bookops-marc/compare/0.5.0...v0.6.0
[0.5.0]: https://github.com/BookOps-CAT/bookops-marc/compare/0.4.0...0.5.0
[0.4.0]: https://github.com/BookOps-CAT/bookops-marc/compare/0.3.0...0.4.0
[0.3.0]: https://github.com/BookOps-CAT/bookops-marc/compare/v0.2.0...0.3.0
[0.2.0]: https://github.com/BookOps-CAT/bookops-marc/compare/v0.1.0...v0.2.0