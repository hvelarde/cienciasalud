# This Python file uses the following encoding: utf-8

"""Based on Martin Aspeli's 'borg' test suite

$Id: base.py 56774 2008-01-11 05:42:02Z hvelarde $
"""

from Testing import ZopeTestCase

# Let Zope know about the two products we require above-and-beyond a basic
# Plone install (PloneTestCase takes care of these).
ZopeTestCase.installProduct('nitf4plone')

# Import PloneTestCase - this registers more products with Zope as a side effect
from Products.PloneTestCase.PloneTestCase import PloneTestCase
from Products.PloneTestCase.PloneTestCase import FunctionalTestCase
from Products.PloneTestCase.PloneTestCase import setupPloneSite

# Set up a Plone site and apply extension profiles
setupPloneSite(products=('nitf4plone',))

class ExtenderTestCase(PloneTestCase):
    """Base class for integration tests for the 'nitf4plone' product. This may
    provide specific set-up and tear-down operations, or provide convenience
    methods.
    """

class ExtenderFunctionalTestCase(FunctionalTestCase):
    """Base class for functional integration tests for the 'nitf4plone' product. 
    This may provide specific set-up and tear-down operations, or provide 
    convenience methods.
    """
