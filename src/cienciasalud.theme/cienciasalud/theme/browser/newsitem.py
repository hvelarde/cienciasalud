# This Python file uses the following encoding: utf-8

from Products.Five.browser import BrowserView

class MainStory(BrowserView):
    title = u'Nota principal'

class Story(BrowserView):
    title = u'Nota secundaria'

class Image(BrowserView):
    title = u'Imagen'

