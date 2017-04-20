from django.contrib import admin
from .models import *

# Register your models here.
@admin.register(TextUpload)
class TextUploadAdmin(admin.ModelAdmin):
    fieldsets = [
        ('File information', {'fields': [('filename', 'language', 'creation')]}),
        (None,               {'fields': ['text']}),
        ('Cache',            {'fields': ['text_cache'], 'classes': ['collapse']})
    ]

    list_display = ['__str__', 'language', 'creation']
    list_filter  = ['creation', 'language']
    search_fields = ['text', 'filename']

    def save_model(self, request, obj, form, change):
        obj.update_cache()
        obj.save()

@admin.register(FileUpload)
class FileUploadAdmin(admin.ModelAdmin):
    pass
