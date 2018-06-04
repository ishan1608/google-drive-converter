from django.http import HttpResponseBadRequest
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import View

from .forms import DriveUrlForm
from .models import DriveJob


class IndexView(View):

    def get(self, request, *args, **kwargs):
        form = DriveUrlForm()
        context = {
            'form': form
        }
        return render(request=request, template_name='converter/index.html', context=context)

    def post(self, request):
        form = DriveUrlForm(request.POST)

        drive_job = None
        success = False
        if form.is_valid():
            drive_job = form.save()
            success = True

        context = {
            'form': form,
            'success': success,
            'status_url': reverse('converter:status', args=(drive_job.id,))
        }

        return render(request=request, template_name='converter/index.html', context=context)


class StatusView(View):
    def get(self, request, id, *args, **kwargs):
        drive_job = DriveJob.objects.filter(id=id).first()
        if not drive_job:
            return HttpResponseBadRequest('Job ID: {} not found'.format(id))
        context = {
            'id': id,
            'drive_job': drive_job
        }
        return render(request=request, template_name='converter/status.html', context=context)