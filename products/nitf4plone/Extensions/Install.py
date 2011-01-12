# This Python file uses the following encoding: utf-8

"""
$Id: Install.py 55432 2007-12-13 04:46:09Z hvelarde $
"""

from cStringIO import StringIO

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import getFSVersionTuple
from Products.ATContentTypes.interface import IATNewsItem

from Products.nitf4plone.extender import NITFExtender
from archetypes.schemaextender.interfaces import IOrderableSchemaExtender

def install(self):
    out = StringIO()
    tool = getToolByName(self, 'portal_setup')
    qi = getToolByName(self, 'portal_quickinstaller')
    url_tool = getToolByName(self, 'portal_url')
    portal = url_tool.getPortalObject()

    if getFSVersionTuple()[:3]>=(3,0,0):
        # Install local adapter support
        sm = portal.getSiteManager()
        sm.registerAdapter(NITFExtender, 
                           (IATNewsItem,),
                           IOrderableSchemaExtender,
                           )

        print >>out, 'Adapter registered'
        tool.runAllImportStepsFromProfile('profile-Products.nitf4plone:default', purge_old=False)
        qi.notifyInstalled('nitf4plone')
        print >>out, 'Profile installed'
    else:
        # Plone 2.5.x
        # adapter already registered globally

        plone_base_profileid = "profile-CMFPlone:plone"
        tool.setImportContext(plone_base_profileid)
        tool.setImportContext('profile-Products.nitf4plone:default')
        tool.runAllImportSteps(purge_old=False)
        tool.setImportContext(plone_base_profileid)
        print >>out, 'Profile installed'

    return out.getvalue()


def uninstall(self):
    out = StringIO()
    tool = getToolByName(self, 'portal_setup')
    qi = getToolByName(self, 'portal_quickinstaller')
    url_tool = getToolByName(self, 'portal_url')
    portal = url_tool.getPortalObject()
    
    if getFSVersionTuple()[:3]>=(3,0,0):
        sm = portal.getSiteManager()
        sm.unregisterAdapter(NITFExtender, 
                             required=None, 
                             provided=IOrderableSchemaExtender)

        print >>out, 'Adapter unregistered'
    else:
        # is not posible to unregister an adapter in Plone 2.5
        print >>out, 'It is not possible to unregister an adapter in Zope 2.9 '

    return out.getvalue()
