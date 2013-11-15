from django.contrib.auth.models import User
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.forms import ModelForm

from simplenote.models import BasicNote

class NoteEditForm(forms.Form):
    title = forms.CharField(widget=forms.TextInput())
    content = forms.CharField(widget=forms.Textarea())

