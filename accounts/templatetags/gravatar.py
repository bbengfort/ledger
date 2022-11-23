# accounts.templatetags.gravatar
# Helpers for user profile images
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Sat Dec 28 15:58:52 2019 -0600
#
# ID: gravatar.py [] benjamin@bengfort.com $

"""
Helpers for user profile images.

TODO: move to profiles specific app when created.
"""

##########################################################################
## Imports
##########################################################################

from hashlib import md5
from django import template

register = template.Library()


##########################################################################
## Template Tags
##########################################################################

@register.filter(name='gravatar')
def gravatar(user, size=35):
    email = str(user.email.strip().lower()).encode('utf-8')
    email_hash = md5(email).hexdigest()
    url = "//www.gravatar.com/avatar/{0}?s={1}&d=identicon&r=PG"
    return url.format(email_hash, size)
