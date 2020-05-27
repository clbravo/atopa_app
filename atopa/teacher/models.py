# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


# TODO, campos reales
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rol = models.TextField(max_length=30)
    nombre = models.CharField(max_length=20, default='')
    apellidos = models.CharField(max_length=50, default='')
    colegio = models.CharField(max_length=50, default='')
    evaluacion = models.BooleanField(default = False)

    def get(self):
        return str(self.nombre)



class Year(models.Model):
    school_year = models.CharField(max_length=32, unique=True)
    current = models.BooleanField(default = False)

    def __str__(self):
        return str(self.school_year)
