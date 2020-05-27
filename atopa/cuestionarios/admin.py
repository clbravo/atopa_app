# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from cuestionarios import models

# Register your models here.
admin.site.register(models.Grupo_edad)
admin.site.register(models.Tipo_pregunta)
admin.site.register(models.Pregunta)
admin.site.register(models.Test)
