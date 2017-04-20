from django.db import models
from django.utils import timezone
from django.urls import reverse
import pygments
from pygments import highlight
from pygments.lexers import get_lexer_by_name, get_lexer_for_filename
from pygments.formatters import HtmlFormatter
import uuid

# Create your models here.
class TextUploadManager(models.Manager):
    def create_text(self, text, language="", filename=None):
        textupload = self.create(text=text, language=language, filename=filename)
        textupload.update_cache()
        return textupload


class TextUpload(models.Model):
    text = models.TextField()
    text_cache = models.TextField(blank=True, null=True)
    language = models.CharField(blank=True, null=True, max_length=64)
    filename = models.CharField(blank=True, null=True, max_length=256)
    creation = models.DateTimeField(default=timezone.now)
    uuid = models.UUIDField(editable=False, unique=True, default=uuid.uuid4)
    
    objects = TextUploadManager()

    def update_cache(self):
        try:
            if self.language == "" and self.filename is not None:
                lexer = get_lexer_for_filename(self.filename, stripall=True)
            else:
                lexer = get_lexer_by_name(self.language, stripall=True)
        except pygments.util.ClassNotFound:
            lexer = get_lexer_by_name("text")

        self.text_cache = highlight(self.text, lexer, HtmlFormatter(linenos=True))

    def get_html(self):
        if self.text_cache is None:
            self.update_cache()
        return self.text_cache

    def __str__(self):
        return self.filename or str(self.uuid)

    def get_absolute_url(self):
        return reverse('pastes:paste', kwargs={'uuid': self.uuid})


def get_file_path(instance, filename):
    if len(filename.split('.')) != 1:
        ext = '.' + filename.split('.')[-1]
        f = ".".join(filename.split('.')[:-1])
    else:
        ext = ''
        f = filename
    # TODO: Use instance's uuid
    return f + ':' + str(uuid.uuid4()) + ext

class FileUpload(models.Model):
    title = models.CharField(max_length=256, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    creation = models.DateTimeField(default=timezone.now)
    uuid = models.UUIDField(editable=False, unique=True, default=uuid.uuid4)
    
    file = models.FileField(upload_to=get_file_path)

    def __str__(self):
        return self.title or str(self.uuid)
    
    def get_absolute_url(self):
        return reverse('pastes:viewfile', kwargs={'uuid': self.uuid})

    def get_original_file(self):
        if len(self.file.name.split('.')) != 1:
            ext = '.' + self.file.name.split('.')[-1]
        else:
            ext = ''
        return ":".join(self.file.name.split(':')[:-1]) + ext

    def get_download_name(self):
        if ".".join(self.get_original_file().split(".")[:-1]) != "":
            return self.get_original_file()
        if self.title.strip() != "":
            if len(self.file.name.split('.')) != 1:
                ext = '.' + self.file.name.split('.')[-1]
            else:
                ext = ''
            return self.title.lower().replace(" ", "-") + ext
        return self.file.name
