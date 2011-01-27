from five import grok
from plone.app.layout.viewlets.interfaces import IAboveContentBody
#from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile

from Acquisition import Implicit
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

class NewsMediaContainer(Implicit, grok.Container):
    grok.implements(IMediaContainer)

class INewsItemMedia(Interface):
    """ Marker interface for news-item media. """

@grok.adapter(IATNewsItem)
@grok.implementer(IMediaContainer)
def news_to_media(news_item):
    return news_item.media

class MediaForNews(grok.Adapter):
    grok.provides(INewsItemMedia)
    grok.context(IATNewsItem)

    def __init__(self, context):
        self.context = context
        if not self.hasContainer():
            self.createContainer()

    def hasContainer(self):
        media = getattr(self.context, 'media', None)
        return media is not None

    def createContainer(self):
        media = getattr(self.context, 'media', None)
        if media is None:
            media = NewsMediaContainer()
            setattr(self.context, 'media', media)

    def getContents(self):
        if not self.hasContainer():
            return []
        return self.context.media.keys()

    def getMediaContainer(self):
        if self.hasContainer():
            return self.context.media

class MediaContainerView(grok.View):
    grok.context(IMediaContainer)
    grok.name('index')

    def render(self):
        return u'%s' % (list(self.context.keys()))


class MediaList(grok.View):
    grok.context(IATNewsItem)

    def render(self):
        on = getattr(self, 'on', None)
        return u'Media Container %s' % on

    def publishTraverse(self, request, name):
        self.traverse_subpath = request.getTraversalStack() + [name]
        request.setTraversalStack([])
        media = INewsItemMedia(self.context).getMediaContainer()
        proxy = location.LocationProxy(media, self.context.__name__, 'media')
        self.on = u'on'
        return zope.location.location.located(proxy, self.context, 'media')

class MediaView(grok.View):
    grok.context(IMediaContainer)

    def render(self):
        return u'Media Container'

    def __getitem__(self, name):
        return getattr(self.context, name, self.context)

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
