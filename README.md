# Ledger

[![Build Status](https://travis-ci.com/bbengfort/ledger.svg?branch=master)](https://travis-ci.com/bbengfort/ledger)
[![Coverage Status](https://coveralls.io/repos/github/bbengfort/ledger/badge.svg?branch=master)](https://coveralls.io/github/bbengfort/ledger?branch=master)

**Bengfort household financial analysis tools.**

## Releases

Ledger has a long history and not that many associated releases (unfortunately). However, with the recent revisions to version 1.4 (the release that implemented Beagle) and the inclusion of Sentry monitoring, I've formalized the release cycle.

Most work will happen in the `develop` branch. When ready to release and deploy to Heroku, we'll bump the version and merge to `master`, and tag the version. Only the master branch will be pushed to Heroku. One pushed to Heroku, run the `scripts/sentry_release.sh` in the Heroku environment to associate the commits and the release with Sentry.

## Testing

Run the tests using `pytest`; note that the test configuration is stored in `pytest.ini` and that the `flake8` checker is written as part of the tests. The pytest-django module is used to discover tests in each indvididual app. Note that the tests in the app are generally stored in a `tests` directory, or if the app is small (or incomplete) in a `test.py` file.