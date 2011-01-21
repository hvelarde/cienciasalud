from five import grok
from plone.app.layout.viewlets.interfaces import IAboveContentBody
#from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile

from Products.ATContentTypes.interfaces import IATNewsItem

from zope.interface import Interface
from zope.schema import BytesLine
from zope.schema import Bytes
from zope.schema import TextLine
from zope.container.interfaces import INameChooser

from OFS.Image import Image
from zope.location import location

grok.context(IATNewsItem)

class IFile(Interface):
    title = TextLine(
            title = u'Content Title',
            )

    data = Bytes(
            title=u'Data',
            description=u'The actual content of the object.',
            default='',
            missing_value='',
            required=False,
            )

    def getSize():
        """Return the byte-size of the data of the object."""

class IImage(IFile):
    """This interface defines an Image that can be displayed.
    """
    def getImageSize():
        """Return a tuple (x, y) that describes the dimensions of
           the object.
        """

class IMediaContainer(Interface):
    """ Marker interface for a news-item media container. """

class NewsMediaContainer(grok.Container):
    grok.implements(IMediaContainer)

class INewsItemMedia(Interface):
    """ Marker interface for news-item media. """

class MediaForNews(grok.Adapter):
    grok.provides(INewsItemMedia)
    grok.context(IATNewsItem)

    def __init__(self, context):
        self.context = context
        if not self.hasContainer():
            self.createContainer()

    def hasContainer(self):
        media = getattr(self.context, '_media', None)
        return media is not None

    def createContainer(self):
        media = getattr(self.context, '_media', None)
        if media is None:
            media = NewsMediaContainer()
            setattr(self.context, '_media', media)

    def getContents(self):
        if not self.hasContainer():
            return []
        return self.context._media.keys()

    def getMediaContainer(self):
        if self.hasContainer():
            return self.context._media

class Media(grok.View):
    grok.context(IATNewsItem)

    def publishTraverse(self, request, name):
        self.traverse_subpath = request.getTraversalStack() + [name]
        request.setTraversalStack([])
        return zope.location.location.located(INewsItemMedia(self.context).getMediaContainer(), self.context, 'media')

class BaseViewlet(grok.Viewlet):
    grok.viewletmanager(IAboveContentBody)
    grok.template('baseviewlet')

    def update(self):
        newsmedia = INewsItemMedia(self.context)
        self.newsmedia = newsmedia

    def imageList(self):
        pass

class AddFileForm(grok.AddForm):
    grok.context(IATNewsItem)
    grok.name(u'add_media')

    form_fields = grok.AutoFields(IFile).select('data')
    template = grok.PageTemplateFile('newsmedia_templates/default_edit_form.pt')

    def update(self):
        newsmedia = INewsItemMedia(self.context)
        if not newsmedia.hasContainer():
            newsmedia.createContainer()
        self.context = newsmedia.getMediaContainer()
        self.newsmedia = newsmedia

    def getContents(self):
        return self.context

    @grok.action(u'Subir archivo')
    def add(self, data):
        if len(data) > 0:
            self.upload(data)
        self.redirect(self.url(self.context))

    def upload(self, data):
        fileupload = self.request['form.data']
        if fileupload and fileupload.filename:
            contenttype = fileupload.headers.get('Content-Type')
            filename = INameChooser(self.context).chooseName(fileupload.filename, None)
            file_ = Image(filename, filename, data, contenttype)
            self.context[filename] = file_
