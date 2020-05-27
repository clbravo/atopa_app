# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import csv

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.shortcuts import render
from .models import Alumno, AlumnoForm, Clase, ClaseForm, Grupo_edad
from .forms import FileForm
from django.contrib.auth.models import User
from .services import upload_student_to_server, delete_class_from_server
from cuestionarios.models import Test
from cuestionarios.forms import LoginUploadForm
from teacher.models import Year
from django.views.generic.list import ListView
from django.views.generic.edit import UpdateView, DeleteView
from datetime import datetime
import io
from django.utils.translation import ugettext, gettext
from builtins import str
from django.utils.translation import ugettext_lazy as _
import os.path

import logging

log = logging.getLogger(__name__)


@login_required
def ListAll(request, id):
    info = dict()
    teacher = User.objects.get(username=request.user)
    year = Year.objects.get(id=int(id))
    clases = Clase.objects.filter(teacher_id=teacher, year_id=year)
    for num, clase in enumerate(clases):
        alumnos = Alumno.objects.filter(clase_id=clase)
        alumnos_clase = []
        for alumno in alumnos:
            alumnos_clase.append(alumno)
        info[num] = {clase: [alumnos_clase, FileForm()]}
    if 'correct' in request.session:
        request.session.modified = True
        alert = 1
        if 'error' not in request.session:
            if request.session['correct'] == 1:
                log.info(1)
                msg = gettext("Se han importado los alumnos correctamente")
            else:
                msg = gettext("Hay un error de formato en el archivo")
        else:
            if request.session['correct'] == 1:
                log.info(1)
                msg = gettext("Se han importado los alumnos. Algunos alumnos no han podido ser importados. Compruebe cuáles son en el archivo ~/atopa/atopa_app/atopa/alumnos_no_importados.txt")
            else:
                msg = gettext("Hay un error de formato en el archivo")
            del request.session['error']
        del request.session['correct']
    else:
        alert = 0
        msg = ''

    return render(request, 'alumnos/list.html', {"info": info, 'year': int(id), 'alert': alert, 'msg':msg})


class AlumnoUpdate(UpdateView):
    model = Alumno
    template_name_suffix = '_update_form'
    fields = ['nombre', 'apellidos', 'alias', 'DNI',
              'fecha_nacimiento', 'sexo']
    pk_url_kwarg = 'id'

    def get_context_data(self, **kwargs):
        context = super(AlumnoUpdate, self).get_context_data(**kwargs)
        context['year'] = self.kwargs['year']
        return context

    def get_success_url(self):
        return reverse('estudiantes', kwargs={'id': self.kwargs['year']})

class AlumnoDelete(DeleteView):
    model = Alumno
    success_url = reverse_lazy('estudiantes')
    pk_url_kwarg = 'id'

    def get_context_data(self, **kwargs):
        context = super(AlumnoDelete, self).get_context_data(**kwargs)
        context['year'] = self.kwargs['year']
        return context

    def get_success_url(self):
        return reverse('estudiantes', kwargs={'id': self.kwargs['year']})


class ClaseUpdate(UpdateView):
    model = Clase
    template_name_suffix = '_update_form'
    fields = ['nombre','grupo_edad']
    pk_url_kwarg = 'id'

    def get_context_data(self, **kwargs):
        context = super(ClaseUpdate, self).get_context_data(**kwargs)
        context['year'] = self.kwargs['year']
        return context

    def get_success_url(self):
        return reverse('estudiantes', kwargs={'id': self.kwargs['year']})
    
class ClaseUpdate2(UpdateView):
    model = Clase
    template_name_suffix = '_update_form'
    fields = ['nombre']
    pk_url_kwarg = 'id'

    def get_context_data(self, **kwargs):
        context = super(ClaseUpdate2, self).get_context_data(**kwargs)
        context['year'] = self.kwargs['year']
        return context

    def get_success_url(self):
        return reverse('estudiantes', kwargs={'id': self.kwargs['year']})

@login_required
def claseDelete(request, id, year):
    clase = Clase.objects.get(pk=id)
    tests = Test.objects.filter(clase=clase, closed=False, uploaded=True)
    if request.method == 'POST':
        form = LoginUploadForm(request.POST)
        try:
            if form.is_valid():
                delete_class_from_server(clase, form)
                clase.delete()
                return HttpResponseRedirect(reverse('estudiantes', kwargs={'id': int(year)}))
        except:
            return HttpResponseRedirect(reverse('noservertest', kwargs={'year': int(year)}))
    else:
        if (tests.count() > 0):
            form = LoginUploadForm()
        else:
            clase.delete()
            return HttpResponseRedirect(reverse('estudiantes', kwargs={'id': int(year)}))
    return render(request,
                  'alumnos/classdelete.html',
                  {'form': form, 'clase': id, 'year': int(year)})

@login_required
def upload_student(request, form, year, clase):
    if not form:
        form = LoginUploadForm()
    request.session['clase'] = int(clase)
    request.session['update'] = 0
    return render(request,
                  'alumnos/alumnoup.html',
                  {'form': form, 'year': int(year)})

@login_required
def crear_alumno(request, year):
    if request.method == 'POST' and 'clase' in request.session:
        clase = Clase.objects.get(id=request.session['clase'])
        student = Alumno(clase_id=clase)
        if 'update' in request.session:
            if request.session['update'] == 1:
                form = AlumnoForm(request.POST, instance=student,clase=request.session['clase'])
                if form.is_valid():
                    tests = Test.objects.filter(clase=clase, closed=False, uploaded=True)
                    if (tests.count() > 0):
                        student = form.save(commit=False)
                        request.session['nombre'] = student.nombre
                        request.session['apellidos'] = student.apellidos
                        request.session['alias'] = student.alias
                        request.session['dni'] = student.DNI
                        request.session['fecha'] = student.fecha_nacimiento.strftime("%d/%m/%y")
                        request.session['sexo'] = student.sexo
                        return upload_student(request, None, year, request.session['clase'])
                    else:
                        student = form.save(commit=False)
                        student.clase_id = clase
                        student.save()
                        return HttpResponseRedirect(reverse('estudiantes', kwargs={'id': int(year)}))
            else:
                formAux = LoginUploadForm(request.POST)
                try:
                    if formAux.is_valid():
                        if 'nombre' in request.session:
                            student = Alumno()
                            student.nombre = request.session['nombre']
                            student.apellidos = request.session['apellidos']
                            student.alias = request.session['alias']
                            student.DNI = request.session['dni']
                            student.fecha_nacimiento = datetime.strptime(request.session['fecha'], "%d/%m/%y")
                            student.sexo = request.session['sexo']
                            student.clase_id = clase
                            student.save()
                            upload_student_to_server(student, formAux)
                            return HttpResponseRedirect(reverse('estudiantes', kwargs={'id': int(year)}))
                    else:
                        return upload_student(request, formAux, year,request.session['clase'])
                except:
                    return HttpResponseRedirect(reverse('noservertest', kwargs={'year': int(year)}))
        else:
            form = AlumnoForm(clase=int(request.session['clase']))
    else:
        form = AlumnoForm(clase=int(request.GET.get('clase')))
        if request.GET.get('clase'):
            request.session['clase'] = int(request.GET.get('clase'))
            request.session['update'] = 1
    return render(request, 'alumnos/alumnocrearform.html', {'form': form, 'year': int(year)})

def noserver(request,year):
    return render(request,
                  'noserver.html',
                  {'test': 0, 'year': int(year)})

@login_required
def crear_clase(request, year):
    if request.method == 'POST':
        form = ClaseForm(request.POST)
        if form.is_valid():
            teacher = User.objects.get(username=request.user)
            clase = form.save(commit=False)
            clase.teacher = teacher
            clase.year = Year.objects.get(id=int(year))
            clase.save()
            return HttpResponseRedirect(reverse('estudiantes', kwargs={'id': int(year)}))
        else:
            return render(request, 'alumnos/clasecrearform.html', {'form': form, 'year': int(year)})
    else:
        form = ClaseForm()
        return render(request, 'alumnos/clasecrearform.html', {'form': form, 'year': int(year)})

@login_required
def importar_alumnos(request, year):
    if request.method == 'POST':
        csvFileName = request.FILES['file']
        log.info(csvFileName)

        if not csvFileName:
            return HttpResponseRedirect(reverse('estudiantes', kwargs={'id': int(year)}))

        decoded_file = csvFileName.read().decode('utf-8').splitlines()
        reader = csv.DictReader(decoded_file)
        try:
            for row in reader:
                newAlumno = Alumno()
                newAlumno.nombre = row['NOMBRE']
                newAlumno.apellidos = row['APELLIDO1'] + " " + row['APELLIDO2']
                newAlumno.alias = newAlumno.nombre + " " + newAlumno.apellidos[0:2]
                newAlumno.DNI = row['DNI']
                date = row['FECHA-NACIMIENTO'].split('/')
                newAlumno.fecha_nacimiento = date[2] + '-' + date[1] + '-' + date[0]
                newAlumno.clase_id_id = request.GET.get('clase')
                if (row['SEXO'] == 'M'):
                    newAlumno.sexo = 'H'
                elif (row['SEXO'] == 'F'):
                    newAlumno.sexo = 'M'
                try:
                    newAlumno.save() # Si es valido se guarda en la base de datos
                except Exception as e:
                    print ("No se puede importar el alumno: " + newAlumno.nombre + " " + newAlumno.apellidos)
                    request.session['error'] = 1
                    with open("alumnos_no_importados.txt", mode="a") as f:
                        f.write("No se puede importar el alumno: " + newAlumno.nombre + " " + newAlumno.apellidos + ": "+ str(e) + '\n')

        except Exception as e:
            log.info(e)
            with open("alumnos_no_importados.txt", mode="a") as f:
                f.write(datetime.now().strftime("%d/%m/%y %H:%M") + '\n')
                f.write("Formato incorrecto" + ": "+ str(e) + '\n')
                request.session['correct'] = 0
            return HttpResponseRedirect(reverse('estudiantes', kwargs={'id': int(year)}))
        request.session['correct'] = 1
        return HttpResponseRedirect(reverse('estudiantes', kwargs={'id': int(year)}))
