# Ledger

[![Build Status](https://travis-ci.com/bbengfort/ledger.svg?branch=master)](https://travis-ci.com/bbengfort/ledger)
[![Coverage Status](https://coveralls.io/repos/github/bbengfort/ledger/badge.svg?branch=master)](https://coveralls.io/github/bbengfort/ledger?branch=master)

**Bengfort household financial analysis tools.**

## Testing

Run the tests using `pytest`; note that the test configuration is stored in `pytest.ini` and that the `flake8` checker is written as part of the tests. The pytest-django module is used to discover tests in each indvididual app. Note that the tests in the app are generally stored in a `tests` directory, or if the app is small (or incomplete) in a `test.py` file.