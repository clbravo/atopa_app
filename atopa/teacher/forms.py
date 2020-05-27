# -*- coding: utf-8 -*-
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils.translation import ugettext, gettext
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import SetPasswordForm
import logging
log = logging.getLogger(__name__)


class SignUpForm(UserCreationForm):
    nombre = forms.CharField(max_length=30,
                             required=True, label=ugettext('Nombre'), help_text=gettext('Obligatorio'),widget=forms.TextInput(attrs={'onchange': 'changename();'}))
    apellidos = forms.CharField(max_length=30,
                                required=True, label=ugettext('Apellidos'), help_text=gettext('Obligatorio'),widget=forms.TextInput(attrs={'onchange': 'changename();'}))
    email = forms.EmailField(max_length=254,
                             help_text=gettext('Obligatorio. Introduzca una dirección de correo válida'))
    colegio = forms.CharField(max_length=254, label=ugettext('Colegio'), help_text=gettext('Obligatorio'))
    evaluacion = forms.BooleanField(required=False,initial=False, label=ugettext('Voy a participar en la evaluación de la aplicación ATOPA'))

    class Meta:
        model = User
        fields = ('username', 'nombre', 'apellidos',
                  'email', 'colegio', 'password1', 'password2','evaluacion')

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)
        self.fields['username'].help_text = gettext('Obligatorio. 150 caracteres como máximo. Únicamente letras, dígitos y @, ., +, -, _')
        self.fields['password1'].help_text = gettext('8 caracteres como mínimo. Debe tener letras y dígitos')
        self.fields['password2'].help_text = gettext('Para verificar, introduzca la misma contraseña anterior')


    def clean_email(self):
        email = self.cleaned_data['email']
        if email:
            if email != '':
                if User.objects.filter(email=email).exists():
                    raise ValidationError(gettext('Ya existe un usuario con ese email'))
        return email

    def clean_username(self):
        username = self.cleaned_data['username']
        if username:
            if username != '':
                if len(username) > 150:
                    raise ValidationError(gettext('El nombre de usuario es demasiado largo'))
        return username

    def clean_password1(self):
        password1 = self.cleaned_data['password1']
        if password1:
            if password1 != '':
                if len(password1) < 8:
                    raise ValidationError(gettext('La contraseña es demasiado corta'))
        return password1
    
class PasswordForm(SetPasswordForm):

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(PasswordForm, self).__init__(user,*args, **kwargs)
        self.fields['new_password1'].help_text = gettext('8 caracteres como mínimo. Debe tener letras y dígitos')
        self.fields['new_password2'].help_text = gettext('Para verificar, introduzca la misma contraseña anterior')

    def clean_password1(self):
        password1 = self.cleaned_data['new_password1']
        if password1:
            if password1 != '':
                if len(password1) < 8:
                    raise ValidationError(gettext('La contraseña es demasiado corta'))
        return password1
