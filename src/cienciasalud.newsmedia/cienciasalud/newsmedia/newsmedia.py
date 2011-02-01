import datetime
import pytz
import urllib
import math

from five import grok
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from plone.app.layout.viewlets.interfaces import IAboveContentBody
#from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile

from Acquisition import Implicit
from Acquisition import aq_inner
from Acquisition import aq_parent
from Products.ATContentTypes.interfaces import IATNewsItem

from zope.interface import Interface
from zope.interface.common import idatetime
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

class INewsMediaLayer(IDefaultBrowserLayer):
   """ Default Layer for News Media Items """

class IImage(Interface):
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

class MediaImage(Image):
    grok.implements(IImage)

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
    grok.layer(INewsMediaLayer)

    def update(self):
        self.redirect(self.url(self.context.__parent__))

    def render(self):
        return u''

class AddFileForm(grok.AddForm):
    grok.context(IATNewsItem)
    grok.name(u'add_media')
    grok.require('cmf.AddPortalContent')
    grok.layer(INewsMediaLayer)

    form_fields = grok.AutoFields(IImage).select('data')
    template = grok.PageTemplateFile('newsmedia_templates/default_edit_form.pt')

    def update(self):
        self.newsmedia = IMediaContainer(self.context)

    def getContents(self):
        return self.context

    @grok.action(u'Subir archivo')
    def add(self, **data):
        if len(data['data']) > 0:
            self.upload(**data)
        self.redirect(self.url(self.context)+'/add_media')

    def upload(self, **data):
        fileupload = self.request['form.data']
        if fileupload and fileupload.filename:
            contenttype = fileupload.headers.get('Content-Type')
            asciiname = filenamenormalizer.normalize(text=fileupload.filename, locale=self.request.locale.getLocaleID())
            filename = INameChooser(self.newsmedia).chooseName(asciiname, None)
            caption = filename
            #if not data['title']:
            #    caption = filename
            #else:
            #    caption = data['title']
            file_ = MediaImage(filename, caption, data['data'], contenttype)
            self.newsmedia[filename] = file_

class EditImageForm(grok.EditForm):
    grok.context(IImage)
    grok.name(u'edit')
    grok.require('cmf.ModifyPortalContent')
    grok.layer(INewsMediaLayer)

    form_fields = grok.AutoFields(IImage)
    template = grok.PageTemplateFile('newsmedia_templates/default_edit_form.pt')

class DeleteImage(grok.View):
    grok.context(IATNewsItem)
    grok.require('zope2.DeleteObjects')
    grok.layer(INewsMediaLayer)

    def render(self):
        filename = urllib.unquote(self.request.get('QUERY_STRING'))
        if filename and filename in self.context['media']:
            del self.context['media'][filename]
            self.redirect(self.url(self.context, 'add_media'))

class BaseViewlet(grok.Viewlet):
    grok.viewletmanager(IAboveContentBody)
    grok.template('baseviewlet')
    grok.require('zope2.View')
    grok.layer(INewsMediaLayer)

    def update(self):
        newsmedia = INewsItemMedia(self.context)
        self.newsmedia = newsmedia

    def imageRows(self, cols, keys):
        rows = []
        if not cols or not keys:
            return rows
        rows_number = int(math.ceil(float(len(keys))/float(cols)))
        for row in range(rows_number):
            this_row = []
            start = row*int(cols)
            end = start + int(cols) 
            for key in keys[start:end]:
                this_row.append(key)
            rows.append(this_row)
        return rows

class BaseImageView(grok.View):
    grok.baseclass()
    grok.context(Image)
    grok.layer(INewsMediaLayer)
    size = ()

    def render(self):
        thumb, format = self.scale(*self.size)
        img = self._make_image(file=thumb, format=format)
        imgd = img.__of__(aq_parent(aq_inner(self.context)))
        return imgd.index_html(self.request, self.response)

    def _make_image(self, file='', format=''):
        """Image content factory"""
        id = self.context.__name__
        title = self.context.title
        mimetype = 'image/%s' % format.lower()
        return MediaImage(id, title, file, mimetype)

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

class ImageThumbView(BaseImageView):
    grok.name('thumb')
    grok.require('zope2.View')
    size = (90, 90)

class ImageLargeView(BaseImageView):
    grok.name('large')
    grok.require('zope2.View')
    size = (768, 768)

class ImageMiniView(BaseImageView):
    grok.name('mini')
    grok.require('zope2.View')
    size = (192, 192)
