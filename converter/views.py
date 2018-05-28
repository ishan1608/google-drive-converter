from django.shortcuts import render
from django.views.generic import View
from .forms import DriveUrlForm


class IndexView(View):

    def get(self, request, *args, **kwargs):
        form = DriveUrlForm()
        context = {
            'form': form
        }
        return render(request=request, template_name='converter/index.html', context=context)

    def post(self, request):
        form = DriveUrlForm(request.POST)

        message = ''
        success = False
        if form.is_valid():
            message = form.save()
            success = True

        context = {
            'form': form,
            'success': success,
            'message': message
        }

        return render(request=request, template_name='converter/index.html', context=context)