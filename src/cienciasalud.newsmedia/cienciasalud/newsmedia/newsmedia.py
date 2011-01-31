from five import grok
from plone.app.layout.viewlets.interfaces import IAboveContentBody
#from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile

from Acquisition import Implicit
from Acquisition import aq_inner
from Acquisition import aq_parent
from Products.ATContentTypes.interfaces import IATNewsItem

from zope.interface import Interface
from zope.schema import BytesLine
from zope.schema import Bytes
from zope.schema import TextLine
from zope.container.interfaces import INameChooser
from plone.i18n.normalizer import filenamenormalizer

from OFS.Image import Image

from cStringIO import StringIO
try:
    import PIL.Image
except ImportError:
    # no PIL, no scaled versions!
    HAS_PIL = False
    PIL_ALGO = None
else:
    HAS_PIL = True
    PIL_ALGO = PIL.Image.ANTIALIAS

_marker = []


grok.context(IATNewsItem)

class IFile(Interface):
    title = TextLine(
            title = u'Titulo de la imagen',
            default=u'',
            missing_value=u'',
            required=False,
            )

    data = Bytes(
            title=u'Image',
            description=u'The actual content of the object.',
            default='',
            missing_value='',
            required=False,
            )

class IMediaContainer(Interface):
    """ Marker interface for a news-item media container. """

class NewsMediaContainer(Implicit, grok.Container):
    grok.implements(IMediaContainer)
    id = __name__ = 'media'

class INewsItemMedia(Interface):
    """ Marker interface for news-item media. """

@grok.adapter(IATNewsItem)
@grok.implementer(IMediaContainer)
def news_to_media(news_item):
    return INewsItemMedia(news_item).getMediaContainer()

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
    grok.require('zope2.View')

    def update(self):
        self.redirect(self.url(self.context.__parent__))

class AddFileForm(grok.AddForm):
    grok.context(IATNewsItem)
    grok.name(u'add_media')
    grok.require('cmf.AddPortalContent')

    form_fields = grok.AutoFields(IFile)
    template = grok.PageTemplateFile('newsmedia_templates/default_edit_form.pt')

    def update(self):
        self.newsmedia = IMediaContainer(self.context)

    def getContents(self):
        return self.context

    @grok.action(u'Subir archivo')
    def add(self, **data):
        if len(data['data']) > 0:
            self.upload(**data)
        self.redirect(self.url(self.context))

    def upload(self, **data):
        fileupload = self.request['form.data']
        if fileupload and fileupload.filename:
            contenttype = fileupload.headers.get('Content-Type')
            asciiname = filenamenormalizer.normalize(fileupload.filename)
            filename = INameChooser(self.newsmedia).chooseName(asciiname, None)
            if not data['title']:
                caption = filename
            else:
                caption = data['title']
            file_ = Image(filename, caption, data['data'], contenttype)
            self.newsmedia[filename] = file_

class BaseViewlet(grok.Viewlet):
    grok.viewletmanager(IAboveContentBody)
    grok.template('baseviewlet')
    grok.require('zope2.View')

    def update(self):
        newsmedia = INewsItemMedia(self.context)
        self.newsmedia = newsmedia

    def imageLists(self, thumb_size=(200,200), big_size=(768,768)):
        thumblist = []
        biglist = []
        return thumblist, biglist

class ImageThumbView(grok.View):
    grok.context(Image)
    grok.name('thumb')
    grok.require('zope2.View')

    def render(self):
        thumb, format = self.scale(w=200, h=200)
        img = self._make_image(file=thumb, format=format)
        imgd = img.__of__(aq_parent(aq_inner(self.context)))
        return imgd.index_html(self.request, self.response)

    def _make_image(self, file='', format=''):
        """Image content factory"""
        id = self.context.__name__
        title = self.context.title
        mimetype = 'image/%s' % format.lower()
        return Image(id, title, file, mimetype)

    def scale(self, w, h, default_format = 'PNG'):
        """ scale image (with material from ImageTag_Hotfix)"""
        #make sure we have valid int's
        size = int(w), int(h)
        data = str(self.context.data)

        original_file=StringIO(data)
        image = PIL.Image.open(original_file)
        # consider image mode when scaling
        # source images can be mode '1','L,','P','RGB(A)'
        # convert to greyscale or RGBA before scaling
        # preserve palletted mode (but not pallette)
        # for palletted-only image formats, e.g. GIF
        # PNG compression is OK for RGBA thumbnails
        original_mode = image.mode
        if original_mode == '1':
            image = image.convert('L')
        elif original_mode == 'P':
            image = image.convert('RGBA')
        image.thumbnail(size, PIL_ALGO)
        format = image.format and image.format or default_format
        # decided to only preserve palletted mode
        # for GIF, could also use image.format in ('GIF','PNG')
        if original_mode == 'P' and format == 'GIF':
            image = image.convert('P')
        thumbnail_file = StringIO()
        # quality parameter doesn't affect lossless formats
        image.save(thumbnail_file, format, quality=88)
        thumbnail_file.seek(0)
        return thumbnail_file, format.lower()
