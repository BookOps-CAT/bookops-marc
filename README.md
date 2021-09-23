[![Build Status](https://app.travis-ci.com/BookOps-CAT/bookops-marc.svg?branch=master)](https://app.travis-ci.com/BookOps-CAT/bookops-marc) [![Coverage Status](https://coveralls.io/repos/github/BookOps-CAT/bookops-marc/badge.svg?branch=master)](https://coveralls.io/github/BookOps-CAT/bookops-marc?branch=master) [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

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
> 0.2.0

## Changelog

### 0.2.0 (08/30/2021)
+ added a method for retrieving branch call number as `pymarc.Field`

### 0.3.0 (09/23/2021)
+ added following methods: `lccn` (retrieves LCCN from bib), `overdrive_number` (retrieves Overdrive Reserve ID), and `upc_number` (retrieves UPC from bib)
