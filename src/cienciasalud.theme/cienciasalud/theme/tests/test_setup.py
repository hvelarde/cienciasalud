import unittest

from cienciasalud.theme.config import PROJECTNAME
from cienciasalud.theme.tests.base import TestCase

skins = ('cienciasalud_theme_custom_images',
        'cienciasalud_theme_custom_templates',
        'cienciasalud_theme_styles')

class TestInstall(TestCase):
    """ensure product is properly installed"""

    def test_stylesheets(self):
        self.failUnless('++resource++cienciasalud.theme.stylesheets/main.css' in self.portal.portal_css.getResourceIds())

    def test_skins(self):
        for s in skins:
            self.failUnless(s in self.portal.portal_skins.objectIds())

class TestUninstall(TestCase):
    """ensure product is properly uninstalled"""

    def afterSetUp(self):
        self.qi = getattr(self.portal, 'portal_quickinstaller')
        self.qi.uninstallProducts(products=[PROJECTNAME])

    def test_product_uninstalled(self):
        self.failIf(self.qi.isProductInstalled(PROJECTNAME))

    def test_stylesheets(self):
        self.failIf('++resource++cienciasalud.theme.stylesheets/main.css' in self.portal.portal_css.getResourceIds())

    def test_skins(self):
        for s in skins:
            self.failIf(s in self.portal.portal_skins.objectIds())

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestInstall))
    suite.addTest(unittest.makeSuite(TestUninstall))
    return suite
