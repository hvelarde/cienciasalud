# This Python file uses the following encoding: utf-8

"""
$Id: extender.py 57168 2008-01-19 01:57:31Z hvelarde $
"""

__author__ = 'Héctor Velarde <hvelarde@jornada.com.mx>'
__docformat__ = 'restructuredtext'
__copyright__ = 'Copyright (C) 2007  DEMOS, Desarrollo de Medios, S.A. de C.V.'
__license__  = 'The GNU General Public License version 2 or later'

from archetypes.schemaextender.interfaces import IOrderableSchemaExtender
from archetypes.schemaextender.field import ExtensionField
from Products.Archetypes import atapi
from Products.Archetypes.utils import OrderedDict
from Products.ATContentTypes.interface import IATNewsItem
from Products.CMFCore.utils import getToolByName
from zope.app.exception.interfaces import UserError
from zope.component import adapts
from zope.interface import implements

# need to find out how to use this values from GS
from config import PROPERTIES
from config import URGENCIES

# debug
from zLOG import LOG, DEBUG, INFO

class PropertyField(ExtensionField, atapi.StringField):
    """Subject code property

    nitf/head/tobject/tobject.property/@tobject.property.type
    Includes such items as analysis, feature, and obituary
    """
    def getDefault(self, instance):
        portal_props = getToolByName(instance, 'portal_properties')
        nitf = getattr(portal_props, 'nitf_properties', None)
        if nitf is None or not hasattr(nitf, 'default_property'):
            return ''
        return nitf.default_property

class SectionField(ExtensionField, atapi.StringField):
    """Named section of a publication where a news object appear

    nitf/head/pubdata/@position.section
    such as Science, Sports, Weekend, etc.
    """
    def getDefault(self, instance):
        portal_props = getToolByName(instance, 'portal_properties')
        nitf = getattr(portal_props, 'nitf_properties', None)
        if nitf is None or not hasattr(nitf, 'default_section'):
            return ''
        return nitf.default_section

    def Vocabulary(self, instance):
        portal_props = getToolByName(instance, 'portal_properties')
        nitf = getattr(portal_props, 'nitf_properties', None)
        if nitf is None or not hasattr(nitf, 'sections'):
            raise UserError, 'No sections defined; please add some.'
        return atapi.DisplayList([(x, x) for x in nitf.sections])

class UrgencyField(ExtensionField, atapi.IntegerField):
    """News importance

    nitf/head/docdata/urgency/@ed-urg
    1=most, 5=normal, 8=least
    """
    def getDefault(self, instance):
        portal_props = getToolByName(instance, 'portal_properties')
        nitf = getattr(portal_props, 'nitf_properties', None)
        if nitf is None or not hasattr(nitf, 'default_urgency'):
            return None
        return nitf.default_urgency

class BylineField(ExtensionField, atapi.StringField):
    """Container for byline information

    nitf/body/body.head/byline
    Can either be structured with direct specification of the responsible
    person / entity and their title or unstructured text can be provided
    """

class NITFExtender(object):
    """Adapter to add NITF fields to News Items
    """
    implements(IOrderableSchemaExtender)
    adapts(IATNewsItem)

    fields = [
        PropertyField('property',
            languageIndependent=1,
            enforceVocabulary=1,
            required=1,
            vocabulary=PROPERTIES,
            widget = atapi.SelectionWidget(
                label='Property',
                label_msgid='property',
                description='Subject code property',
                description_msgid='help_property',
                i18n_domain='nitf4plone')),
        SectionField('section',
            languageIndependent=1,
            enforceVocabulary=1,
            required=1,
            widget = atapi.SelectionWidget(
                label='Section',
                label_msgid='section',
                description='Named section where the news object appear',
                description_msgid='help_section',
                i18n_domain='nitf4plone')),
        UrgencyField('urgency',
            languageIndependent=1,
            enforceVocabulary=1,
            required=1,
            vocabulary=URGENCIES,
            widget = atapi.SelectionWidget(
                label='Urgency',
                label_msgid='urgency',
                description='News importance',
                description_msgid='help_urgency',
                i18n_domain='nitf4plone')),
        BylineField('byline',
            languageIndependent=1,
            required=1,
            widget = atapi.StringWidget(
                size=40,
                label='Author',
                label_msgid='byline',
                description='Container for byline information',
                description_msgid='help_byline',
                i18n_domain='nitf4plone')),
        ]

    def __init__(self, context):
        self.context = context

    def getFields(self):
        return self.fields

    def getOrder(self, original):
        # we only need to change the order of the fields in Plone 2.5
        if 'metadata' in original:
            # first we remove the fields from whichever schemata they are
            for schemata in original.keys():
                if 'relatedItems' in original[schemata]:
                    original[schemata].remove('relatedItems')
                if 'subject' in original[schemata]:
                    original[schemata].remove('subject')
            # now we insert them where we want them to appear
            idx = original['default'].index('property')
            original['default'].insert(idx, 'subject')
            original['metadata'].insert(0, 'relatedItems')

        return original
