"""
It is a common pattern for packages to have a user-defined exception hierarchy
with a common base class, in order to make it easier to distinguish between
package logic (i.e. scalegrease) errors and system errors. Error is the base
class, and there are no children yet.

See http://www.network-theory.co.uk/docs/pytut/UserdefinedExceptions.html for
some examples.
"""


class Error(Exception):
    """An exception from within scalegrease-code."""
    pass
