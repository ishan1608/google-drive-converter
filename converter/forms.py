from django.forms import forms


class DriveUrlForm(forms.Form):
    document_url = forms.Field(
        required=True,
        label='URL',
        help_text='Enter the drive URL'
    )

    def save(self):
        return 'Downloading {}'.format(self.cleaned_data['document_url'])
