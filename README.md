![tests](https://github.com/BookOps-CAT/bookops-marc/actions/workflows/unit-tests.yaml/badge.svg?branch=main) [![Coverage Status](https://coveralls.io/repos/github/BookOps-CAT/bookops-marc/badge.svg?branch=main)](https://coveralls.io/github/BookOps-CAT/bookops-marc?branch=main) [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

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

with open('marc.mrc', "rb") as marcfile:
	reader = SierraBibReader(marcfile)
	for bib in reader:
		print(bib.sierra_bib_id_normalized)
		print(bib.sierra_bib_format)
		print(bib.branch_call_no)
		print(bib.orders)
		print(bib.main_entry)
		print(bib.form_of_item)
		print(bib.dewey)
		print(bib.dewey_shortened)
```

In certain scenarios it may be convenient to instantiate a `Bib` directly from an instance of `pymarc.Record`. This can be accomplished using the `Bib.pymarc_record_to_local_bib()` classmethod:

```python
from pymarc import Record
from bookops_marc.bib import pymarc_record_to_local_bib

# pymarc Record instance
record = Record()
bib = Bib.pymarc_record_to_local_bib(record, "bpl")
bib.remove_unsupported_subjects()
```

Python 3.8 and up.

## Version
> 0.12.0

## Changelog
### [0.12.0] - 2024-11-13
#### Added
+ Python 3.13 to unit tests in GitHub actions
+ `OclcNumber` class
  + replaces helper functions previously in from `local_values.py`:
    + `oclcNo_with_prefix`, `oclcNo_without_prefix`, `is_oclc_number`, `has_oclc_prefix`, `_add_oclc_prefix` and `_delete_oclc_prefix`
#### Changed
+ changed most `Bib` methods to properties. This follows the pattern that pymarc uses with managed `Record` attributes:
  + methods changed to properties:
    + `audience`
    + `branch_call_no`
    + `branch_call_no_field`
    + `cataloging_date`
    + `control_number`
    + `created_date`
    + `dewey`
    + `dewey_shortened`
    + `form_of_item`
    + `languages`
    + `lccn`
    + `main_entry`
    + `oclc_nos`
    + `orders`
    + `overdrive_number`
    + `physical_description`
    + `record_type`
    + `sierra_bib_format`
    + `sierra_bib_id`
    + `sierra_bib_id_normalized`
    + `subjects_lc`
    + `suppressed`
    + `upc_number`
  + `normalize_oclc_control_number` and `remove_unsupported_subjects` are still methods as they attributes of a `Bib` object
+ the `pymarc_record_to_local_bib` function is now a `classmethod` for the `Bib` class
+ `Order` is now a class rather than a `NamedTuple`
  + `Order` objects are instantiated from a `Field` object with an optional `following_field` parameter 
#### Removed
+ helper functions in `local_values.py`. the functionality has been retained in the `Bib`, `Order`, and `OclcNumber` class
  
### [0.11.0] - 2024-11-13
#### Changed
+ updated pymarc to 5.2.3
+ updated dev dependencies:
  + pytest (8.3.3)
  + black (24.8.0)
  + mypy (1.13)
+ refactored code to support new `Indicators` class introduced in `pymarc` 5.2.0


## Changelog
### [0.10.0] - 2024-03-16
#### Added
+ method to retrieve all OCLC numbers present in a bib (001, 035, 991): `bib.oclc_nos()`
+ methods to normalize OCLC number in the 001 control field in `bib.Bib` class: `bib.normalize_oclc_control_number`
+ new module `local_values` with the followoing methods:
  + `_add_oclc_prefix`
  + `_delete_oclc_prefix`
  + `has_oclc_prefix`,
  + `is_oclc_number`,
  + `oclcNo_with_prefix`,
  + `oclcNo_without_prefix`
#### Changed
+ dropped Python 3.7 support
+ update dev dependencies:
  + black (24.3.0)
  + mypy (1.9)
  + pytest (8.1.1)
  + pytest-cov (4.1.0)
+ changed `pyproject.toml` settings for black, mypy, & coverage
+ deleted `requirements.txt` and transition to `pyproject.toml` for dependencies
### [0.9.0] - 2024-01-05
#### Changed
+ updated to pymarc 5.0
+ updated dev dependencies:
  + black (22.12.0)
  + pytest (7.4.4)
+ github actions upgrade to v4
#### Added
+ tests for Python 3.11 & 3.12
  

### [0.8.1] - 2022-08-16
#### Fixed
+ version bump propagated to all places


### [0.8.0] - 2022-08-15
#### Added
+ `bib.pymarc_record_to_local_bib()` method to instage `Bib` instance from `pymarc.Record` instance
+ `sierra_bib_format()` method in `Bib` class that returns 998$d of Sierra record

#### Changed
+ added basic normalization to `library` parameter passed to `Bib` class
+ `stub_marc` test fixture renamed to `stub_bib`

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

[0.12.0]:https://github.com/BookOps-CAT/bookops-marc/compare/0.11.0...0.12.0
[0.11.0]:https://github.com/BookOps-CAT/bookops-marc/compare/0.10.0...0.11.0
[0.10.0]:https://github.com/BookOps-CAT/bookops-marc/compare/0.9.0...0.10.0
[0.9.0]: https://github.com/BookOps-CAT/bookops-marc/compare/0.8.1...0.9.0
[0.8.1]: https://github.com/BookOps-CAT/bookops-marc/compare/0.8.0...0.8.1
[0.8.0]: https://github.com/BookOps-CAT/bookops-marc/compare/0.7.0...0.8.0
[0.7.0]: https://github.com/BookOps-CAT/bookops-marc/compare/v0.6.0...0.7.0
[0.6.1]: https://github.com/BookOps-CAT/bookops-marc/compare/v0.6.0...v0.6.1
[0.6.0]: https://github.com/BookOps-CAT/bookops-marc/compare/0.5.0...v0.6.0
[0.5.0]: https://github.com/BookOps-CAT/bookops-marc/compare/0.4.0...0.5.0
[0.4.0]: https://github.com/BookOps-CAT/bookops-marc/compare/0.3.0...0.4.0
[0.3.0]: https://github.com/BookOps-CAT/bookops-marc/compare/v0.2.0...0.3.0
[0.2.0]: https://github.com/BookOps-CAT/bookops-marc/compare/v0.1.0...v0.2.0