# ledger.version
# Helper module for managing versioning information
#
# Author:  Benjamin Bengfort <benjamin@bengfort.com>
# Created: Sat Apr 14 12:07:04 2018 -0400
#
# ID: version.py [36d8a34] benjamin@bengfort.com $

"""
Helper module for managing versioning information
"""

import os
import subprocess


## Commit environment variables
SLUG_COMMIT_ENV = [
    "GIT_REVISION", "HEROKU_SLUG_COMMIT", "SLUG_COMMIT",
]


##########################################################################
## Versioning
##########################################################################

__version_info__ = {
    'major': 1,
    'minor': 4,
    'micro': 4,
    'releaselevel': 'final',
    'serial': 66,
}


def get_version(short=False, revision=False):
    """
    Returns the version from the version info.
    """
    if __version_info__['releaselevel'] not in ('alpha', 'beta', 'final'):
        raise ValueError(
            "unknown release level '{}', select alpha, beta, or final.".format(
                __version_info__['releaselevel']
            )
        )

    vers = ["{major}.{minor}".format(**__version_info__)]

    if __version_info__['micro']:
        vers.append(".{micro}".format(**__version_info__))

    if __version_info__['releaselevel'] != 'final' and not short:
        vers.append('{}{}'.format(__version_info__['releaselevel'][0],
                                  __version_info__['serial']))

    if revision:
        vers.append("@{}".format(get_revision(short=short)))

    return ''.join(vers)


def get_revision(short=False, env=True):
    """
    Returns the latest git revision (sha1 hash).
    """

    # First look up the revision from the environment
    if env:
        for envvar in SLUG_COMMIT_ENV:
            if envvar in os.environ:
                slug = os.environ[envvar]
                if short:
                    return slug[:7]
                return slug

    # Otherwise return the subprocess lookup of the revision
    cmd = ['git', 'rev-parse', 'HEAD']
    if short:
        cmd.insert(2, '--short')

    return subprocess.check_output(cmd).decode('utf-8').strip()


def get_sentry_release():
    return "ledger v{}".format(get_version(short="True", revision=True))
