#!/bin/bash
# This script finalizes a ledger release to Sentry and associates commits.
# It can (and should) be run on Heroku with the heroku run command.

if [ -z "$SENTRY_AUTH_TOKEN" ]; then
    echo "please set SENTRY_AUTH_TOKEN to finalize the release"
    exit 1
fi

if [ -z "$SENTRY_ORG" ]; then
    SENTRY_ORG="bengfort"
fi

VERSION=$(python -c "from ledger.version import get_sentry_release; print(get_sentry_release())")
echo "creating release $VERSION"

sentry-cli releases new -p ledger $VERSION
sentry-cli releases set-commits --auto $VERSION
