# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os

from django.http import HttpResponse
from django.http import JsonResponse
from django.conf import settings
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render

from .forms import ContactForm
from .tasks import send_video_email_task

# Create your views here.
from .models import Video
from core.models import AppConfig


def index(request):
    config = AppConfig.objects.first()
    video_list = Video.objects.all().order_by(config.order_by_field)
    if settings.PAGINATION_PER_PAGE != config.number_of_videos_per_age:
        settings.PAGINATION_PER_PAGE = config.number_of_videos_per_age
    paginator = Paginator(video_list, settings.PAGINATION_PER_PAGE)

    page = request.GET.get('page')
    videos = paginator.get_page(page)
    return render(request, 'index.html', {'videos': videos})


def detail(request, video_id):
    video = get_object_or_404(Video, pk=video_id)

    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            send_video_email_task.delay(form.cleaned_data['email'], video.video_path)

    form = ContactForm()
    return render(request, 'detail.html', {'video': video, 'form': form, 'fullpath': os.path.join(settings.WATCHING_DIR, video.video_path) })


def playback(request):
    if request.method == 'POST':
        Video.objects.all().update(is_playback=False)
        if request.POST['is_playback']:
            video = get_object_or_404(Video, pk=request.POST['pk'])
            video.is_playback = True
            video.save()
        return JsonResponse({'result': True})
    else:
        video = Video.objects.filter(is_playback=True).last()
        if not video:
            video = Video.objects.latest('modified_timestamp')
        return render(request, 'playback.html', {'video': video})
