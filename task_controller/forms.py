from django import forms


class FileFieldForm(forms.Form):
    file = forms.FileField()
