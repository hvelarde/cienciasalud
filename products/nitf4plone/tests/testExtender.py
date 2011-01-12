# This Python file uses the following encoding: utf-8

"""
$Id: testExtender.py 57169 2008-01-19 02:03:58Z hvelarde $
"""

__author__ = 'Héctor Velarde <hvelarde@jornada.com.mx>'
__docformat__ = 'restructuredtext'
__copyright__ = 'Copyright (C) 2007  DEMOS, Desarrollo de Medios, S.A. de C.V.'
__license__  = 'The GNU General Public License version 2 or later'

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Products.PloneTestCase.setup import PLONE25
from Products.PloneTestCase.setup import PLONE30
from Products.nitf4plone import initialize

# Import the base test case classes
from base import ExtenderTestCase

# according to Martin Aspeli, __contains__ on a schema is defined
# such that 'foo' in obj.Schema() will return True if a field with
# name 'foo' is in the schema; this is not working here, that's
# why I have to use getNames() on testStandardFields() and
# testExtendedFields()
from Products.Archetypes.Schema import getNames

class TestNewsItem(ExtenderTestCase):
    """ ensure content type implementation """

    def afterSetUp(self):
        initialize(self) # register adapter in Plone 2.5
        self.folder.invokeFactory('News Item', 'news1')
        self.news1 = getattr(self.folder, 'news1')

    def testIsExtensible(self):
        from archetypes.schemaextender.interfaces import IExtensible
        self.failUnless(IExtensible.providedBy(self.news1))

    def testStandardFields(self):
        standard_fields = ['id', 'title', 'description', 'text', 'image', 'imageCaption', 'relatedItems', 'subject', 'contributors', 'creators', 'effectiveDate', 'expirationDate', 'language', 'rights', 'creation_date', 'modification_date', 'excludeFromNav', 'allowDiscussion']
        schema = getNames(self.news1.Schema())
        for field in standard_fields:
            self.failUnless(field in schema)

    def testExtendedFields(self):
        extended_fields = ['property', 'section', 'urgency', 'byline']
        schema = getNames(self.news1.Schema())
        for field in extended_fields:
            self.failUnless(field in schema)

    def testSchemataFieldsOrder(self):
        schema = self.news1.Schema()

        if PLONE30:
            # default
            expected_order = ['id', 'title', 'description', 'text', 'image', 'imageCaption', 'property', 'section', 'urgency', 'byline']
            order = [f.getName() for f in schema.getSchemataFields('default')]
            self.assertEqual(expected_order, order)

            # categorization
            expected_order = ['subject', 'relatedItems', 'location', 'language']
            order = [f.getName() for f in schema.getSchemataFields('categorization')]
            self.assertEqual(expected_order, order)

            # dates
            expected_order = ['effectiveDate', 'expirationDate', 'creation_date', 'modification_date']
            order = [f.getName() for f in schema.getSchemataFields('dates')]
            self.assertEqual(expected_order, order)

            # ownership
            expected_order = ['creators', 'contributors', 'rights']
            order = [f.getName() for f in schema.getSchemataFields('ownership')]
            self.assertEqual(expected_order, order)

            # settings
            expected_order = ['allowDiscussion', 'excludeFromNav']
            order = [f.getName() for f in schema.getSchemataFields('settings')]
            self.assertEqual(expected_order, order)

        elif PLONE25:
            # default
            expected_order = ['id', 'title', 'description', 'text', 'image', 'imageCaption', 'subject', 'property', 'section', 'urgency', 'byline']
            order = [f.getName() for f in schema.getSchemataFields('default')]
            self.assertEqual(expected_order, order)
    
            # metadata
            expected_order = ['relatedItems', 'contributors', 'creators', 'effectiveDate', 'expirationDate', 'language', 'rights', 'creation_date', 'modification_date', 'excludeFromNav', 'allowDiscussion']
            order = [f.getName() for f in schema.getSchemataFields('metadata')]
            self.assertEqual(expected_order, order)

class TestFields(ExtenderTestCase):
    """ ensure fields implementation """

    def afterSetUp(self):
        self.folder.invokeFactory('News Item', 'news1')
        self.news1 = getattr(self.folder, 'news1')

    def testPropertyField(self):
        schema = self.news1.Schema()
        property_field = schema.getField('property')
        # default method return value is defined in the skin
        self.assertEqual(property_field.getDefault(self.news1), '')
        # getting and setting values
        self.assertEqual(property_field.get(self.news1), '')
        property_field.set(self.news1, 'Current')
        self.assertEqual(property_field.get(self.news1), 'Current')
    
    def testSectionField(self):
        schema = self.news1.Schema()
        section_field = schema.getField('section')
        # default method return value is defined in the skin
        self.assertEqual(section_field.getDefault(self.news1), '')
        # vocabulary is defined in the skin
        from Products.Archetypes.atapi import DisplayList
        self.assertEqual(section_field.Vocabulary(self.news1), DisplayList([]))
        # getting and setting values
        self.assertEqual(section_field.get(self.news1), '')
        section_field.set(self.news1, 'Sports')
        self.assertEqual(section_field.get(self.news1), 'Sports')

    def testUrgencyField(self):
        schema = self.news1.Schema()
        urgency_field = schema.getField('urgency')
        # default method return value is defined in the skin
        self.assertEqual(urgency_field.getDefault(self.news1), '')
        # getting and setting values
        self.assertEqual(urgency_field.get(self.news1), None)
        urgency_field.set(self.news1, 5)
        self.assertEqual(urgency_field.get(self.news1), 5)

    def testBylineField(self):
        schema = self.news1.Schema()
        byline_field = schema.getField('byline')
        # there's no default method defined for byline
        self.assertEqual(byline_field.getDefault(self.news1), '')
        # getting and setting values
        self.assertEqual(byline_field.get(self.news1), '')
        byline_field.set(self.news1, 'someone')
        self.assertEqual(byline_field.get(self.news1), 'someone')

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestNewsItem))
    suite.addTest(makeSuite(TestFields))
    return suite

if __name__ == '__main__':
    framework()
