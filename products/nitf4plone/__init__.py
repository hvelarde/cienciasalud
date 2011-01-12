# This Python file uses the following encoding: utf-8

"""
$Id: Install.py 55432 2007-12-13 04:46:09Z hvelarde $
"""

def initialize(context):
    try:
        from Products.CMFPlone.migrations import v3_0
    except ImportError:
        # Plone 2.5

        from utils import log, WARNING
        log("Products.nitf4plone non-local adapter registrations aren't persistent", severity=WARNING)

        from archetypes.schemaextender.interfaces import IOrderableSchemaExtender
        from zope.component import provideAdapter

        from Products.ATContentTypes.interface import IATNewsItem
        from Products.nitf4plone.extender import NITFExtender

        provideAdapter(NITFExtender, 
                       adapts=(IATNewsItem,),
                       provides=IOrderableSchemaExtender,
                       )

        log("Products.nitf4plone.extender.NITFExtender adapter registered globally")
