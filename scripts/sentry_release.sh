#!/bin/bash
# This script finalizes a ledger release to Sentry and associates commits.
# It can (and should) be run on Heroku with the heroku run command.

if [ -f ".env" ]; then
    export $(grep -v '^#' .env | xargs -0)
    if [ $? -ne 0 ]; then
        echo ".env file may contain spaces in variable, temporarily comment it out with #"
        exit 1
    fi
fi

if [ -z "$SENTRY_AUTH_TOKEN" ]; then
    echo "please set SENTRY_AUTH_TOKEN to finalize the release"
    exit 1
fi

if [ -z "$SENTRY_ORG" ]; then
    export SENTRY_ORG="bengfort"
fi

if [ -z "$SENTRY_ENVIRONMENT" ]; then
    export SENTRY_ENVIRONMENT="production"
fi

ENVIRONMENT="production"
VERSION=$(python -c "from ledger.version import get_sentry_release; print(get_sentry_release())") || exit 1
echo "creating release $VERSION in environment $SENTRY_ENVIRONMENT"

read -p "continue with release [Y/n]? " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "stopping without releasing"
    exit 1
fi

sentry-cli releases new -p ledger "$VERSION"
sentry-cli releases set-commits --auto "$VERSION"
sentry-cli releases finalize "$VERSION"
sentry-cli releases deploys "$VERSION" new -e "$SENTRY_ENVIRONMENT"