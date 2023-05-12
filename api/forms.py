from django import forms
from .models import Customer


class ReviewCreateForm(forms.Form):
    author = forms.CharField()
    email = forms.EmailField()
    text = forms.CharField()
    rate = forms.IntegerField()

