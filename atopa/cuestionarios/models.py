# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import builtins

from alumnos.models import Clase, Alumno
from teacher.models import Year
from django.contrib.auth.models import User
from django.db import models
from django_mysql.models import Model, JSONField
from django.forms import ModelForm, HiddenInput, ChoiceField, Select, IntegerField
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext, gettext
from django.utils.translation import ugettext_lazy as _

import logging

log = logging.getLogger(__name__)

class Tipo_estructura(models.Model):
    tipo = models.CharField(max_length=3)
    descripcion = models.TextField(max_length=300, blank=True)

    def __str__(self):
        return self.descripcion

class Tipo_pregunta(models.Model):
    tipo = models.CharField(max_length=3)
    descripcion = models.TextField(max_length=300, blank=True)

    def __str__(self):
        return self.tipo


class Grupo_edad(models.Model):
    grupoedad = models.CharField(max_length=30)
    franjaedad = models.CharField(max_length=5, default=0)

    def __str__(self):
        return self.grupoedad


class Pregunta(models.Model):
    # Creado la tabla de tipo de preguntas para que sea
    # mas configurable.
    # tipospreguntas = [
    #     ('PGP', 'Percepción del grupo positiva'),
    #     ('PGN', 'Percepción del grupo negativa'),
    #     ('PPP', 'Percepción propia positiva'),
    #     ('PPN', 'Percepción propia negativa'),
    #     ('AAP', 'Asociación de atributos positiva'),
    #     ('AAN', 'Asociación de atributos negativa'),
    #     ]
    pregunta = models.TextField(max_length=500, blank=False)
    tipo_estructura = models.ForeignKey(Tipo_estructura,on_delete=models.CASCADE)
    tipo_pregunta = models.ForeignKey(Tipo_pregunta,
                                      on_delete=models.CASCADE
                                      )
    grupo_edad = models.ForeignKey(Grupo_edad,
                                   on_delete=models.CASCADE)

    def __str__(self):
        return builtins.str(_(self.pregunta))

class Test(Model):
    nombre = models.CharField(max_length=32, unique=True)
    clase = models.ForeignKey(Clase, on_delete=models.CASCADE)
    estructura = models.ForeignKey(Tipo_estructura, on_delete=models.CASCADE)
    date_created = models.DateTimeField(
        verbose_name=_("Creation date"), auto_now_add=True, null=True
    )
    uploaded = models.BooleanField(default = False)
    downloaded = models.BooleanField(default = False)
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    closed = models.BooleanField(default = False)
    year = models.ForeignKey(Year, on_delete=models.CASCADE, null=True)
    first = models.ForeignKey('self', on_delete=models.CASCADE, null=True)
    followUp = models.BooleanField(default = False)
    final = models.BooleanField(default = False)
    remote_id = models.IntegerField(null=True)
    survey1 = models.BooleanField(default = False)
    survey2 = models.BooleanField(default = False)
    def __str__(self):
        return str(self.id)


class Preguntas_test(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE,
                             blank=False)
    pregunta = models.ForeignKey(Pregunta, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.id)


class TestForm(ModelForm):
    class Meta:
        model = Test
        fields = ['nombre', 'clase', 'estructura']

    def clean_nombre(self):
        nombre = self.cleaned_data['nombre']
        if Test.objects.filter(nombre=nombre).exists():
            raise ValidationError(ugettext('Ya existe un test con ese nombre'))
        return nombre
    
    def __init__(self, *args, **kwargs):
        super(TestForm, self).__init__(*args, **kwargs)

        for f in self.fields:
            self.fields[f].label = _(self.fields[f].label)


class Preguntas_testForm(ModelForm):
    class Meta:
        model = Preguntas_test
        fields = ['pregunta']

    def __init__(self, tipo_pregunta, tipo_estructura, grupo_edad,  *args, **kwargs):
        super(Preguntas_testForm, self).__init__(*args, **kwargs)
        
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'

        self.fields['pregunta'].queryset = Pregunta.objects.filter(
            tipo_pregunta=tipo_pregunta)
        # Para los cuatro primeros tipos de preguntas (PGP, PGN, PPP, PPN), solo se muestran las que coincidan con
        # el tipo de estructura del test: formales o informales.
        # Para los dos ultimos tipos de preguntas (ANN, ANP), se muestran todas las preguntas: formales e informales
        if tipo_pregunta.tipo in ('PGP','PGN','PPP','PPN'):
            self.fields['pregunta'].queryset = Pregunta.objects.filter(
                tipo_pregunta=tipo_pregunta, tipo_estructura=tipo_estructura, grupo_edad=grupo_edad)
        else:
            self.fields['pregunta'].queryset = Pregunta.objects.filter(tipo_pregunta=tipo_pregunta, grupo_edad=grupo_edad)
            
    def clean_pregunta(self):
        log.info(self.cleaned_data['pregunta'])
        pregunta = self.cleaned_data['pregunta']
        if not pregunta:
            raise ValidationError(ugettext('Deben cubrirse todas las preguntas'))
        else:
            if pregunta == '':
                raise ValidationError(ugettext('Deben cubrirse todas las preguntas'))
        return pregunta

class AlumnoTests(models.Model):
    idTest = models.ForeignKey(Test, on_delete=models.CASCADE)
    idAl = models.ForeignKey(Alumno, on_delete=models.CASCADE)
    username = models.CharField(primary_key=True,max_length=255, unique=True)
    answer = models.BooleanField(default = False)

    def get_nombre(self):
        student = Alumno.objects.get(id=self.idAl.id)
        return student.nombre

    def get_apellidos(self):
        student = Alumno.objects.get(id=self.idAl.id)
        return student.apellidos
