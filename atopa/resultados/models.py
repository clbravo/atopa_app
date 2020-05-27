# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django_mysql.models import JSONField, Model
from django.db import models

from cuestionarios.models import Preguntas_test, Grupo_edad
from alumnos.models import Alumno


class Respuesta(Model):
    alumno = models.ForeignKey(Alumno,
                               on_delete=models.CASCADE, null=True, blank=True)
    pregunta = models.ForeignKey(Preguntas_test,
                                 on_delete=models.CASCADE)
    respuesta = JSONField()

class Link(Model):
    name = models.TextField(max_length=500, blank=False)
    url = models.TextField(max_length=500, blank=False)
