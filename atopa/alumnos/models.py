# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.forms import ModelForm
from django.contrib.auth.models import User
from teacher.models import Year
from django.utils.translation import ugettext, gettext
from django.core.exceptions import ValidationError
import re
import logging

log = logging.getLogger(__name__)

class Grupo_edad(models.Model):
    grupo_edad = models.CharField(max_length=30)
    franja_edad = models.CharField(max_length=5)

    def __str__(self):
        return self.grupo_edad

class Clase(models.Model):
    nombre = models.CharField(max_length=30, unique=True)
    grupo_edad = models.ForeignKey(Grupo_edad, on_delete=models.CASCADE)
    modify = models.BooleanField(default = True)
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    year = models.ForeignKey(Year, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.nombre


class ClaseForm(ModelForm):
    class Meta:
        model = Clase
        fields = ['nombre','grupo_edad']
        
    
    def clean_nombre(self):
        nombre = self.cleaned_data['nombre']
        if Clase.objects.filter(nombre=nombre).exists():
            raise ValidationError(ugettext('Ya existe una clase con ese nombre'))
        return nombre


class Alumno(models.Model):
    nombre = models.CharField(max_length=20)
    apellidos = models.CharField(max_length=50 )
    alias = models.CharField(max_length=15, null=True, blank=True)
    clase_id = models.ForeignKey(Clase, on_delete=models.CASCADE)
    DNI = models.CharField(max_length=10, null=True, blank=True)
    fecha_nacimiento = models.DateField()
    sexo_pos = [
        ('H', ugettext('Hombre')),
        ('M', ugettext('Mujer')),
        ]
    sexo = models.CharField(max_length=1, choices=sexo_pos)

    class Meta:
        unique_together = ('alias', 'clase_id')
        unique_together = ('DNI', 'clase_id')

    def __str__(self):
        if self.alias:
            return self.alias
        else:
            return self.nombre

    def get_id(self):
        return str(self.id)


class AlumnoForm(ModelForm):
    class Meta:
        model = Alumno
        fields = ['nombre', 'apellidos', 'alias', 'DNI',
                  'fecha_nacimiento', 'sexo']
    
    def __init__(self, *args, **kwargs):
        self.clase = kwargs.pop('clase', None)
        super(AlumnoForm, self).__init__(*args, **kwargs)
        for fieldname in ['nombre', 'apellidos', 'fecha_nacimiento', 'sexo']:
            self.fields[fieldname].help_text = gettext('Obligatorio')
        self.fields['fecha_nacimiento'].help_text += gettext('. Debe ser dd/mm/yyyy')
        
    def clean_DNI(self):
        dni = self.cleaned_data['DNI']
        if dni:
            if dni != '':
                pattern = re.compile("^([0-9]{8})[A-Za-z]{1}$")
                if not pattern.match(dni):
                    raise ValidationError(ugettext('El formato del DNI no es correcto'))
                clase = Clase.objects.get(id=self.clase)
                if Alumno.objects.filter(DNI=dni, clase_id=clase).exists():
                    raise ValidationError(ugettext('Ya existe un alumno con ese DNI'))
        return dni
    
    def clean_alias(self):
        alias = self.cleaned_data['alias']
        if alias:
            if alias != '':
                clase = Clase.objects.get(id=self.clase)
                if Alumno.objects.filter(alias=alias, clase_id=clase).exists():
                    raise ValidationError(ugettext('Ya existe un alumno con ese alias'))
        return alias
