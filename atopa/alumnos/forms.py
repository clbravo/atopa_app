# -*- coding: utf-8 -*-
from django import forms
from .models import Alumno


class AlumnoForm(forms.ModelForm):
    class Meta:
        model = Alumno
        exclude = ('clase_id',)

class FileForm(forms.Form):
    file = forms.FileField(widget=forms.FileInput(attrs={'onchange': 'this.form.submit();', 'accept': '.csv'}))
