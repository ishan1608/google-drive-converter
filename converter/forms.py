from django.forms import forms, ChoiceField

from .models import DriveJob


class DriveUrlForm(forms.Form):
    document_url = forms.Field(
        required=True,
        label='URL',
        help_text='Enter the drive shareable URL'
    )
    quality = ChoiceField(choices=DriveJob.QUALITY_CHOICES, required=True, initial='360p')

    def save(self):
        DriveJob.initialize_job(self.cleaned_data['document_url'], self.cleaned_data['quality'])
