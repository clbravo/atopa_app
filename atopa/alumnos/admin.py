# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from alumnos import models

# Register your models here.
admin.site.register(models.Alumno)
admin.site.register(models.Clase)

