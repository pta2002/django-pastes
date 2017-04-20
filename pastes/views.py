from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .models import *
from sendfile import sendfile
import mimetypes

# Create your views here.
def home(request):
    pastes = TextUpload.objects.all().order_by('-creation')[:50]
    return render(request, 'pastes/home.html', {'pastes': pastes})


def view_paste(request, uuid):
    paste = get_object_or_404(TextUpload, uuid=uuid)
    return render(request, 'pastes/paste.html', {'paste': paste})


def view_raw_paste(request, uuid):
    paste = get_object_or_404(TextUpload, uuid=uuid)
    return HttpResponse(paste.text, content_type='text/text')

def view_file(request, uuid):
    file = get_object_or_404(FileUpload, uuid=uuid)
    mime = mimetypes.guess_type(file.file.path)

    if mime[0] is not None:
        typecat = mime[0].split('/')[0]
    else:
        typecat = 'none'
    if mime[1] is not None:
        return render(request, 'pastes/file.html', {'file': file, 'mime': mime})
    mime = typecat
    if typecat == 'image':
        return render(request, 'pastes/image.html', {'file': file, 'mime': mime})
    elif typecat == 'video':
        return render(request, 'pastes/video.html', {'file': file, 'mime': mime})
    elif typecat == 'audio':
        return render(request, 'pastes/audio.html', {'file': file, 'mime': mime})
    else:
        return render(request, 'pastes/file.html', {'file': file, 'mime': mime})

def download_file(request, uuid):
    file = get_object_or_404(FileUpload, uuid=uuid)
    return sendfile(request, file.file.path, attachment=True, attachment_filename=file.get_download_name())

# API
@csrf_exempt
def api_upload(request):
    errors = []
    if request.method != 'POST':
        return JsonResponse({"errors":["Must use POST"]}, status=400)

    if request.META.get('Authorization', requests.POST.get('token', '')) != getattr(settings, "API_TOKEN", ''):
        errors.append("Invalid auth token")

    if 'file' not in request.FILES:
        errors.append("`file' not sent")

    if errors:
        return JsonResponse({"errors":errors}, status=400)
    else:
        mime = mimetypes.guess_type(request.FILES['file'].name)
        if mime[0] is not None and mime[0].startswith('text/') and mime[1] is None:
            text = request.FILES['file'].read()
            t = TextUpload.objects.create_text(text, filename=request.FILES['file'].name)
            t.save()
        else:
            t = FileUpload(file=request.FILES['file'], title=request.POST.get('title', request.FILES['file'].name), description=request.POST.get('description', ''))
            t.save()
        return JsonResponse({'errors': errors, 'url': t.get_absolute_url()})
