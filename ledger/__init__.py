# ledger
# The primary entry point for the ledger web app.
#
# Author:  Benjamin Bengfort <benjamin@bengfort.com>
# Created: Sat Apr 14 10:19:07 2018 -0400
#
# ID: __init__.py [] benjamin@bengfort.com $

"""
The primary entry point for the ledger web app.
"""

##########################################################################
## Imports
##########################################################################

from .version import get_version, __version_info__

__version__ = get_version()
