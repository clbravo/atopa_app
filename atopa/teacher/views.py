# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import requests

from django.http import HttpResponse,HttpRequest
from django.shortcuts import render,redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from .forms import SignUpForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
import logging
import datetime
from .models import UserProfile, Year
from django.db.models import Count, Q

log = logging.getLogger(__name__)


def register(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        log.debug(form)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            dni = form.cleaned_data.get('DNI')
            colegio = form.cleaned_data.get('colegio')
            nombre = form.cleaned_data.get('nombre')
            apellidos = form.cleaned_data.get('apellidos')
            evaluacion = form.cleaned_data.get('evaluacion')
            user = authenticate(username=username, password=raw_password)
            teacher = UserProfile()
            teacher.user= user
            teacher.rol = 'Profesor'
            teacher.DNI = dni
            teacher.colegio = colegio
            teacher.nombre = nombre
            teacher.apellidos = apellidos
            teacher.evaluacion = evaluacion
            teacher.save()
            login(request, user)
            return HttpResponseRedirect(reverse('home'))
    else:
        form = SignUpForm()
    return render(request, 'teacher/register.html', {'form': form})

@login_required
def menu(request,id):
    return render(request, 'teacher/menu.html', {'year': int(id)})

@login_required
def school_year_list(request):
    years = Year.objects.all().count()
    if years == 0:
        today = datetime.datetime.now()
        if 8 <= today.month <= 12:
            school_year = str(today.year) + "/" + str(today.year+1)
        elif 1 <= today.month <= 7:
            school_year = str(today.year -1) + "/" + str(today.year)
        year = Year()
        year.school_year = school_year
        year.current = True
        year.save()
    else:
        today = datetime.datetime.now()
        if 8 <= today.month <= 12:
            school_year = str(today.year) + "/" + str(today.year+1)
        elif 1 <= today.month <= 7:
            school_year = str(today.year -1) + "/" + str(today.year)
        current_year = Year.objects.get(current=True)
        if current_year.school_year != school_year:
            current_year.current = False
            current_year.save()
            year = Year()
            year.school_year = school_year
            year.current = True
            year.save()
    years = Year.objects.all().annotate(num_tests=Count('test')).filter(Q(num_tests__gt=0) | Q(current=True))
    return render(request, 'teacher/year_list.html', {'years': years})