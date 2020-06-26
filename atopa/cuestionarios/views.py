# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.shortcuts import render
from django.shortcuts import get_object_or_404

from django.views.generic import ListView, DeleteView, UpdateView

from .models import Test, TestForm, Preguntas_testForm, Tipo_pregunta, Preguntas_test, AlumnoTests, Tipo_estructura
from alumnos.models import Alumno
from alumnos.models import Clase
from teacher.models import Year
from django.contrib.auth.models import User
from django.db.models import Count
from django.conf import settings
from django.contrib.auth.decorators import login_required
from cuestionarios.services import upload_to_server, delete_from_server, send_survey1_server, send_survey2_server
from resultados.services import download_from_server
from cuestionarios.forms import LoginUploadForm, Survey1Form, Survey2Form

from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import LETTER
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, inch, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from django.http import HttpResponse
from io import BytesIO
from django.utils.translation import ugettext, gettext

import errno
from socket import error as socket_error
from teacher.models import UserProfile

import logging

log = logging.getLogger(__name__)


@login_required
def ListAll(request,id):
    info = dict()
    teacher = User.objects.get(username=request.user)
    teacherprofile = UserProfile.objects.get(user__username=request.user)
    year = Year.objects.get(id=int(id))
    tests = Test.objects.filter(teacher=teacher, year_id=year)
    for num,test in enumerate(tests):
        alumnos = AlumnoTests.objects.filter(idTest=test)
        alumnos_test = []
        for alumno in alumnos:
            alumnos_test.append(alumno)
        info[num] = {test: alumnos_test}
    if 'download' in request.path:
        idTest = request.path.rsplit('/', 2)[1]
        if Preguntas_test.objects.filter(test_id=Test.objects.get(id=int(idTest))).annotate(num_answers=Count('respuesta')).filter(num_answers__gt=0).count() == 0:
            no = 1
        else:
            no = 0
        confirm = 1
    else:
        confirm = 0
        no = 0
    if 'upload' in request.path:
        confirmUp = 1
    else:
        confirmUp = 0
    return render(request, 'cuestionarios/test_list.html', {"info": info, 'confirm': confirm, 'confirmUp':confirmUp, 'no': no, 'year': int(id), 'eva': teacherprofile.evaluacion})


@login_required
def testDelete(request, id, year):
    teacher = UserProfile.objects.get(user__username=request.user)
    quiz = Test.objects.get(pk=id)
    if request.method == 'POST':
        form = LoginUploadForm(request.POST)
        try:
            if form.is_valid():
                delete_from_server(quiz, form, True)
                if quiz.first:
                    quiz.first.final = False
                    quiz.first.followUp = False
                    quiz.first.save()
                quiz.delete()
                return HttpResponseRedirect(reverse('testlist', kwargs={'id':int(year)}))
        except Exception as e:
            log.info(e)
            return noserver(request,year)
    else:
        if not quiz.closed and quiz.uploaded:
            form = LoginUploadForm()
        else:
            if quiz.first:
                quiz.first.final = False
                quiz.first.followUp = False
                quiz.first.save()
            quiz.delete()
            return HttpResponseRedirect(reverse('testlist', kwargs={'id':int(year)}))
    return render(request,
                  'cuestionarios/testdelete.html',
                  {'form': form, 'cuestionario': id, 'year': year})


@login_required
def survey1(request, id, year):
    teacher = UserProfile.objects.get(user__username=request.user)
    quiz = Test.objects.get(pk=id)
    if request.method == 'POST':
        form = Survey1Form(request.POST)
        try:
            if form.is_valid():
                problem = send_survey1_server(quiz, form)
                if problem == 1:
                    return noserver(request,year)
                return HttpResponseRedirect(reverse('testlist', kwargs={'id':int(year)}))
        except Exception as e:
            log.info(e)
            return noserver(request,year)
    else:
        form = Survey1Form()
    return render(request,
                  'cuestionarios/survey1.html',
                  {'form': form, 'cuestionario': id, 'year': year})

@login_required
def survey2(request, id, year):
    teacher = UserProfile.objects.get(user__username=request.user)
    quiz = Test.objects.get(pk=id)
    if request.method == 'POST':
        form = Survey2Form(request.POST)
        try:
            if form.is_valid():
                problem = send_survey2_server(quiz, form)
                if problem == 1:
                    return noserver(request,year)
                return HttpResponseRedirect(reverse('testlist', kwargs={'id':int(year)}))
        except Exception as e:
            log.info(e)
            return noserver(request,year)
    else:
        form = Survey2Form()
    return render(request,
                  'cuestionarios/survey2.html',
                  {'form': form, 'cuestionario': id, 'year': year})


@login_required
def secondTest(request, id, year):
    teacher = UserProfile.objects.get(user__username=request.user)
    quiz = Test.objects.get(pk=id)
    quizSecond = Test()
    quizSecond.clase = quiz.clase
    quizSecond.estructura = quiz.estructura
    quizSecond.teacher = quiz.teacher
    quizSecond.nombre = quiz.nombre + " - " + ugettext("Seguimiento")
    quizSecond.year = quiz.year
    quizSecond.first = quiz
    quizSecond.followUp = True
    quizSecond.save()
    quiz.followUp = True
    quiz.final = True
    quiz.save()
    preguntas = Preguntas_test.objects.filter(test=quiz)
    for p in preguntas:
        pregunta = Preguntas_test()
        pregunta.test = quizSecond
        pregunta.pregunta = p.pregunta
        pregunta.save()
    return HttpResponseRedirect(reverse('testlist', kwargs={'id':int(year)}))

@login_required
def testClose(request, id, year):
    teacher = UserProfile.objects.get(user__username=request.user)
    if request.method == 'POST':
        quiz = Test.objects.get(pk=id)
        form = LoginUploadForm(request.POST)
        try:
            if form.is_valid():
                delete_from_server(quiz, form, False)
                return HttpResponseRedirect(reverse('testlist', kwargs={'id':int(year)}))
        except Exception as e:
            log.info(e)
            return noserver(request,year)
    else:
        form = LoginUploadForm()
    return render(request,
                  'cuestionarios/testclose.html',
                  {'form': form, 'cuestionario': id, 'year': year})


class TestUpdate(UpdateView):
    model = Test
    template_name_suffix = '_update_form'
    fields = ['nombre', 'estructura']
    pk_url_kwarg = 'id'
    second_form = Preguntas_testForm

    def get_context_data(self, **kwargs):
        context = super(TestUpdate, self).get_context_data(**kwargs)
        context['preguntas'] = Preguntas_test.objects.filter(test=self.object)
        context['year'] = self.kwargs['year']
        return context

    def get_success_url(self):
        teacher = UserProfile.objects.get(user__username=self.request.user)
        return reverse('testlist', kwargs={'id': self.kwargs['year']})

@login_required
def update_preguntas_test(request, id,year):
    teacher = UserProfile.objects.get(user__username=request.user)
    tiposPregunta = Tipo_pregunta.objects.all()
    test = Test.objects.get(pk=int(id))
    preguntas = Preguntas_test.objects.filter(test=test)
    if request.method == 'POST':
        tipoEstructura = test.estructura
        grupoEdad = test.clase.grupo_edad_id
        preguntasForm = dict()
        check = False
        for tipoPregunta in tiposPregunta:
            preguntasform = Preguntas_testForm(
                tipoPregunta, tipoEstructura, grupoEdad,
                request.POST, prefix=str(tipoPregunta),
                instance=Preguntas_test())
            if not preguntasform.is_valid():
                check = True
            preguntasForm[tipoPregunta] = preguntasform
        if not check:
            for p in preguntas:
                if tipoPregunta == p.pregunta.tipo_pregunta:
                    pregunta = preguntasform.save(commit=False)
                    pregunta.id = p.id
                    pregunta.test = test
                    pregunta.save()
            return HttpResponseRedirect(reverse('testlist', kwargs={'id':int(year)}))

    else:
        tipoEstructura = test.estructura
        grupoEdad = test.clase.grupo_edad_id
        preguntasForm = dict()
        for tipoPregunta in tiposPregunta:
            pre = Preguntas_test()
            for p in preguntas:
                if tipoPregunta == p.pregunta.tipo_pregunta:
                    pre = p
            preguntasForm[tipoPregunta] = Preguntas_testForm(
                tipoPregunta, tipoEstructura, grupoEdad,
                instance=Preguntas_test(),
                prefix=str(tipoPregunta),
                initial={'pregunta': int(pre.pregunta.id)})
    return render(request, 'cuestionarios/testpreguntasform.html',
                  {'preguntasForm': preguntasForm, 'year': int(year)})


@login_required
def crear_test(request,id):
    if request.method == 'POST':
        testform = TestForm(request.POST)
        teacher = User.objects.get(username=request.user)
        testform.fields['clase'].queryset=Clase.objects.filter(teacher_id=teacher).annotate(num_students=Count('alumno')).filter(num_students__gte=3)
        if testform.is_valid():
            request.session['nombre'] = str(request.POST.__getitem__('nombre'))
            clase = request.POST.__getitem__('clase')
            estructura = request.POST.__getitem__('estructura')
            return HttpResponseRedirect(reverse('crear_preguntas_test',kwargs={'clase':clase,'estructura':estructura, 'id': int(id)}))
    else:
        testform = TestForm()
        teacher = User.objects.get(username=request.user)
        testform.fields['clase'].queryset=Clase.objects.filter(teacher_id=teacher).annotate(num_students=Count('alumno')).filter(num_students__gte=3)

    return render(request, 'cuestionarios/testform.html',
                  {'form': testform, 'year':int(id)})


@login_required
def crear_preguntas_test(request, clase, estructura, id):
    tiposPregunta = Tipo_pregunta.objects.all()
    teacherprofile = UserProfile.objects.get(user__username=request.user)
    if request.method == 'POST':
        tipoEstructura = Tipo_estructura.objects.get(id=estructura)
        grupoEdad = Clase.objects.get(id=clase).grupo_edad_id
        check = False
        preguntasForm = dict()
        for tipoPregunta in tiposPregunta:
            preguntasform = Preguntas_testForm(
                tipoPregunta, tipoEstructura, grupoEdad,
                request.POST, prefix=str(tipoPregunta),
                instance=Preguntas_test())
            if not preguntasform.is_valid():
                check = True
            preguntasForm[tipoPregunta] = preguntasform
        if not check:
            test = Test()
            teacher = User.objects.get(username=request.user)
            test.nombre = request.session['nombre']
            test.teacher = teacher
            test.estructura = tipoEstructura
            test.clase = Clase.objects.get(id=clase)
            test.year= Year.objects.get(id=int(id))
            test.save()
            for t in preguntasForm:
                pre = preguntasForm[t].save(commit=False)
                pre.test = test
                pre.save()
            return HttpResponseRedirect(reverse('testlist', kwargs={'id':int(id)}))

    else:
        tipoEstructura = estructura
        grupoEdad = Clase.objects.get(id=clase).grupo_edad_id
        preguntasForm = dict()
        for tipoPregunta in tiposPregunta:
            preguntasForm[tipoPregunta] = Preguntas_testForm(
                tipoPregunta, tipoEstructura, grupoEdad,
                instance=Preguntas_test(),
                prefix=str(tipoPregunta))
                # initial={'test': int(request.session['test'])})
    return render(request, 'cuestionarios/testpreguntasform.html',
                    {'preguntasForm': preguntasForm, 'year':int(id)})


@login_required
def testupload(request, id, year):
    if request.method == 'POST':
        quiz = Test.objects.get(pk=id)
        form = LoginUploadForm(request.POST)
        try:
            if form.is_valid():
                upload_to_server(quiz, form)
                return ListAll(request, int(year))
        except Exception as e:
            log.info(e)
            return noserver(request,year)
    else:
        form = LoginUploadForm()
    return render(request,
                  'cuestionarios/testuploadconfirm.html',
                  {'form': form, 'cuestionario': id, 'year': int(year)})

def noserver(request,year):
    return render(request,
                  'noserver.html',
                  {'test': 1, 'year':year})

@login_required
def testdownload(request, id, year):
    if request.method == 'POST':
        quiz = Test.objects.get(pk=id)
        form = LoginUploadForm(request.POST)
        try:
            if form.is_valid():
                download_from_server(quiz, form)
                return ListAll(request, int(year))
        except:
            return noserver(request,year)
    else:
        form = LoginUploadForm()
    return render(request,
                  'cuestionarios/testdownloadconfirm.html',
                  {'form': form, 'cuestionario': id, 'year':int(year)})

class FooterCanvas(canvas.Canvas):

    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self.pages = []

    def showPage(self):
        self.pages.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        page_count = len(self.pages)
        for page in self.pages:
            self.__dict__.update(page)
            self.draw_canvas(page_count)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_canvas(self, page_count):
        page =  str(self._pageNumber) + " de " + str(page_count)
        self.saveState()
        self.setStrokeColorRGB(0, 0, 0)
        self.setLineWidth(0.5)
        self.line(40, 38, 800, 38)
        self.setFont('Helvetica', 10)
        self.drawString(700, 25, page)
        self.drawImage(settings.STATICFILES_DIRS[0] + ("/topomenunegro.png"), 25,525, width=80, height=60, mask='auto')
        self.drawImage(settings.STATICFILES_DIRS[0] + ("/teavilogograndecontacto.jpg"), 625,510, width=131, height=60, mask='auto')
        self.line(40,510, 800, 510)
        self.restoreState()

@login_required
def codedownload(request, id):
   cuestionario = Test.objects.get(id=id)
   response = HttpResponse(content_type='application/pdf')
   response['Content-Disposition'] = 'attachement; filename="codigos-cuestionario-{0}.pdf"'.format(cuestionario.nombre)

   buffer = BytesIO()
   doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30,leftMargin=30, topMargin=100,bottomMargin=50)
   doc.pagesize = landscape(A4)
   elements = []

   data = [
   ["Nombre", "Apellidos", "Alias", "DNI", "Fecha de nacimiento", "Sexo", "Código"],
   ]

   alumnos = AlumnoTests.objects.filter(idTest=cuestionario)
   for al in alumnos:
        student = Alumno.objects.get(id=al.idAl.id)
        if student.alias:
            alias = student.alias
        else:
            alias = ''
        if student.DNI:
            dni = student.DNI
        else:
            dni = ''
        data.append([student.nombre,student.apellidos,alias,dni, student.fecha_nacimiento.strftime("%d/%m/%Y"), student.sexo, str(al.username)])
   log.debug(data)
   style = TableStyle([
       ('FONT', (0, 0), (0, -1), 'Helvetica-BoldOblique'),
       ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold'),
       # ('INNERGRID', (0, 0), (-1, -1), 0.50, colors.white),
       # ('BOX', (0,0), (-1,-1), 0.25, colors.white),
       ('LINEBELOW', (0, 1), (-1, -2), 0.25, colors.gray),
       ('LINEBELOW', (0, 0), (-1, 0), 1, colors.gray),
       ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
       ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
       ('LINEABOVE', (0,0), (-1,0), 1, colors.white)
   ])

   #Configure style and word wrap
   s = getSampleStyleSheet()
   s = s['BodyText']
   s.wordWrap = 'CJK'
   s.fontName = 'Helvetica-Bold'
   data2 = []
   for r, row in enumerate(data):
       aux = []
       for c, cell in enumerate(row):
           if c == 0 and (1 <= r <= len(data) - 1):
               s.fontName = 'Helvetica-Oblique'
           elif (0 <= c <= len(row) -1) and r == 0:
               s.fontName = 'Helvetica-Bold'
           else:
               s.fontName = 'Helvetica'
           s.fontSize = 9
           aux.append(Paragraph(cell, s))
       data2.append(aux)
   #data2 = [[Paragraph(cell, s) for cell in row] for row in data]
   t=Table(data2)
   t.setStyle(style)

   #Send the data and build the file
   elements.append(t)
   doc.multiBuild(elements, canvasmaker=FooterCanvas)
   pdf = buffer.getvalue()
   buffer.close()
   response.write(pdf)

   return response

