# Ledger

[![CI](https://github.com/bbengfort/ledger/actions/workflows/tests.yaml/badge.svg?branch=develop)](https://github.com/bbengfort/ledger/actions/workflows/tests.yaml)
[![CD](https://github.com/bbengfort/ledger/actions/workflows/containers.yaml/badge.svg?branch=develop)](https://github.com/bbengfort/ledger/actions/workflows/containers.yaml)

**Bengfort household financial analysis tools.**

## Releases

Ledger has a long history and not that many associated releases (unfortunately). However, with the recent revisions to version 1.4 (the release that implemented Beagle) and the inclusion of Sentry monitoring, I've formalized the release cycle.

Most work will happen in the `develop` branch. When ready to release and deploy to Heroku, we'll bump the version and merge to `master`, and tag the version. Only the master branch will be pushed to Heroku. One pushed to Heroku, run the `scripts/sentry_release.sh` in the Heroku environment to associate the commits and the release with Sentry.

Starting from the develop branch, consider the relase for version 1.0

```
$ git checkout -b release-1.0
```

Edit the `ledger/version.py` file with the new version information. Run the tests.

```
$ git checkout master
$ git merge --no-ff --no-edit release-1.0
$ git tag -a v1.0
$ git push origin v1.0
$ git push heroku master
$ ./scripts/sentry_release.sh
```

This should finalize the release, which will now be in both GitHub, Sentry, and Heroku.

```
$ git checkout develop
$ git merge --no-ff --no-edit release-1.0
$ git branch -d release 1.0
```

Now the develop branch should be updated with the new version information.

## Testing

Run the tests using `pytest`; note that the test configuration is stored in `pytest.ini` and that the `flake8` checker is written as part of the tests. The pytest-django module is used to discover tests in each indvididual app. Note that the tests in the app are generally stored in a `tests` directory, or if the app is small (or incomplete) in a `test.py` file.