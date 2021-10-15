# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, redirect

import json
from django.contrib.auth.decorators import login_required
from cuestionarios.models import Test, Preguntas_test, AlumnoTests, Grupo_edad
from django.contrib.auth.models import User
from django.template.defaultfilters import register
from reportlab.graphics.shapes import Drawing, Line
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from .models import Respuesta, Link
import math
import copy
from django.conf import settings
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, inch, portrait, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, ListFlowable, ListItem, PageBreak, \
    Flowable, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from django.http import HttpResponse
from django.utils.translation import ugettext, gettext
from io import BytesIO

import logging

from teacher.models import UserProfile

log = logging.getLogger(__name__)
MAX_POINTS = 5
MIN_POINTS = 1
MIDDLE_POINT = int(round((MAX_POINTS + MIN_POINTS)/2))

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
        self.line(30, 38, 550, 38)
        self.setFont('Helvetica', 10)
        self.drawString(500, 25, page)
        self.drawImage(settings.STATICFILES_DIRS[0] + ("/topomenunegro.png"), 25,760, width=80, height=60, mask='auto')
        self.drawImage(settings.STATICFILES_DIRS[0] + ("/teavilogograndecontacto.jpg"),425,755, width=131, height=60, mask='auto')
        self.line(30, 750, 550, 750)
        self.restoreState()

@login_required
def show_results(request, test, year):
    teacher = UserProfile.objects.get(user__username=str(request.user))
    test = Test.objects.get(id=test)
    preguntas = Preguntas_test.objects.filter(test=test)
    alumnos = AlumnoTests.objects.filter(idTest=test)
    als = {}
    for a in alumnos:
        als[a.get_nombre() + " " + a.get_apellidos()] = str(a.username)
    matrix = {}
    for num, pregunta in enumerate(preguntas):
        question = {}
        for respuesta in Respuesta.objects.filter(pregunta=pregunta):
            student = AlumnoTests.objects.get(idAl=respuesta.alumno.id, idTest=test)
            j = json.loads(respuesta.respuesta)
            answers = {}
            for element in j:
                if 'text' not in element:
                    answers[j.get(element)] = {str('#000000'): str((MIDDLE_POINT - int(element)) + MIDDLE_POINT)}
            for e,a in enumerate(alumnos):
                if str(a.username) == str(student.username) or a.username not in answers:
                    answers[a.username] = {str('#000000'): str('')}
            question[student.username] = answers
        matrix[num+1] = question
    sp = {}
    spval = {}
    np = {}
    sn = {}
    snval = {}
    nn = {}
    ip = {}
    ipval = {}
    imp = {}
    iN = {}
    inval = {}
    imn = {}
    ipp = {}
    ipval5 = {}
    ipn = {}
    inval6 = {}
    matrix12 = {}
    matrix34 = {}
    for m in matrix:
        for answer in matrix[m]:
            if str(answer) not in matrix12:
                matrix12[str(answer)] = {}
            if 'EP' not in matrix12[str(answer)]:
                matrix12[str(answer)]['EP'] = 0
            if 'EN' not in matrix12[str(answer)]:
                matrix12[str(answer)]['EN'] = 0
            if 'RP' not in matrix12[str(answer)]:
                matrix12[str(answer)]['RP'] = 0
            if 'RN' not in matrix12[str(answer)]:
                matrix12[str(answer)]['RN'] = 0
            if str(answer) not in matrix34:
                matrix34[str(answer)] = {}
            if 'PP' not in matrix34[str(answer)]:
                matrix34[str(answer)]['PP'] = 0
            if 'PAP' not in matrix34[str(answer)]:
                matrix34[str(answer)]['PAP'] = 0
            if 'PN' not in matrix34[str(answer)]:
                matrix34[str(answer)]['PN'] = 0
            if 'PAN' not in matrix34[str(answer)]:
                matrix34[str(answer)]['PAN'] = 0
            for student in matrix[m][answer]:
                if student not in sp:
                    sp[student] = 0
                if student not in spval:
                    spval[student] = 0
                if student not in sn:
                    sn[student] = 0
                if student not in snval:
                    snval[student] = 0
                if student not in ip:
                    ip[student] = 0
                if student not in ipval:
                    ipval[student] = 0
                if student not in iN:
                    iN[student] = 0
                if student not in inval:
                    inval[student] = 0
                if student not in ipp:
                    ipp[student] = 0
                if student not in ipn:
                    ipn[student] = 0
                if student not in ipval5:
                    ipval5[student] = 0
                if student not in inval6:
                    inval6[student] = 0
                if matrix[m][answer][student] != {str('#000000'): str('')}:
                    if m == 1:
                        matrix12[str(answer)]['EP'] += 1
                        sp[student] += 1
                        spval[student] += int(matrix[m][answer][student][list(matrix[m][answer][student])[0]])
                        if student in matrix[m]:
                            if matrix[m][student][answer] != {str('#000000'): str('')}:
                                matrix12[str(answer)]['RP'] += 1

                                if '#000000' in matrix[m][answer][student]:
                                    matrix[m][answer][student]['#d6c22b'] = matrix[m][answer][student]['#000000']
                                    del matrix[m][answer][student]['#000000']
                                if '#000000' in matrix[m][student][answer]:
                                    matrix[m][student][answer][str('#d6c22b')] = matrix[m][student][answer]['#000000']
                                    del matrix[m][student][answer]['#000000']
                            if matrix[m + 1][student][answer] != {str('#000000'): str('')}:
                                if '#000000' in matrix[m][answer][student]:
                                    matrix[m][answer][student][str('#e05ab8')] = matrix[m][answer][student]['#000000']
                                    del matrix[m][answer][student]['#000000']
                                if '#000000' in matrix[m+1][student][answer]:
                                    matrix[m+1][student][answer][str('#e05ab8')] = matrix[m+1][student][answer]['#000000']
                                    del matrix[m+1][student][answer]['#000000']
                    elif m == 2:
                        matrix12[str(answer)]['EN'] += 1
                        sn[student] += 1
                        snval[student] += int(matrix[m][answer][student][list(matrix[m][answer][student])[0]])
                        if student in matrix[m]:
                            if matrix[m][student][answer] != {str('#000000'): str('')}:
                                matrix12[str(answer)]['RN'] += 1

                                if '#000000' in matrix[m][answer][student]:
                                    matrix[m][answer][student][str('#0da863')] = matrix[m][answer][student]['#000000']
                                    del matrix[m][answer][student]['#000000']
                                if '#000000' in matrix[m][student][answer]:
                                    matrix[m][student][answer][str('#0da863')] = matrix[m][student][answer]['#000000']
                                    del matrix[m][student][answer]['#000000']
                    elif m == 3:
                        ip[student] += 1
                        ipval[student] += int(matrix[m][answer][student][list(matrix[m][answer][student])[0]])
                        matrix34[str(answer)]['PP'] += 1
                        if student in matrix[m]:
                            if matrix[m-2][student][answer] != {str('#000000'): str('')}:
                                matrix34[str(answer)]['PAP'] += 1
                                if '#000000' in matrix[m][answer][student]:
                                    matrix[m][answer][student][str('#349beb')] = matrix[m][answer][student]['#000000']
                                    del matrix[m][answer][student]['#000000']
                            elif matrix[m-1][student][answer] != {str('#000000'): str('')}:
                                if '#000000' in matrix[m][answer][student]:
                                    matrix[m][answer][student][str('#ed3e46')] = matrix[m][answer][student]['#000000']
                                    del matrix[m][answer][student]['#000000']
                    elif m == 4:
                        iN[student] += 1
                        inval[student] += int(matrix[m][answer][student][list(matrix[m][answer][student])[0]])
                        matrix34[str(answer)]['PN'] += 1
                        if student in matrix[m]:
                            if matrix[m-2][student][answer] != {str('#000000'): str('')}:
                                matrix34[str(answer)]['PAN'] += 1
                                if '#000000' in matrix[m][answer][student]:
                                    matrix[m][answer][student][str('#eb8034')] = matrix[m][answer][student]['#000000']
                                    del matrix[m][answer][student]['#000000']
                            elif matrix[m-3][student][answer] != {str('#000000'): str('')}:
                                if '#000000' in matrix[m][answer][student]:
                                    matrix[m][answer][student][str('#9646e0')] = matrix[m][answer][student]['#000000']
                                    del matrix[m][answer][student]['#000000']
                    elif m == 5:
                        ipval5[student] += int(matrix[m][answer][student][list(matrix[m][answer][student])[0]])
                    elif m == 6:
                        inval6[student] += int(matrix[m][answer][student][list(matrix[m][answer][student])[0]])

    n = len(alumnos)

    data1 = {}
    data1[1] = {'d': float(sum(sp.values())) / n}
    data1[2] = {'p': float(data1[1]['d']) / (n-1)}
    data1[3] = {'qq': 1 - data1[2]['p']}
    data1[4] = {'M': data1[2]['p'] * (n-1)}
    data1[5] = {'ss': math.sqrt((n-1)*data1[2]['p']*data1[3]['qq'])}
    if data1[5]['ss'] != 0:
        data1[6] = {'a': (data1[3]['qq']-data1[2]['p'])/data1[5]['ss']}
    else:
        data1[6] = {'a': 0}
    data1[7] = {'Xsup': data1[4]['M'] + get_t(data1[6]['a'], False)*data1[5]['ss']}
    data1[8] = {'Xinf': data1[4]['M'] + get_t(data1[6]['a'], True)*data1[5]['ss']}

    data2 = {}
    data2[1] = {'d': float(sum(sn.values())) / n}
    data2[2] = {'p': float(data2[1]['d']) / (n-1)}
    data2[3] = {'qq': 1 - data2[2]['p']}
    data2[4] = {'M': data2[2]['p'] * (n-1)}
    data2[5] = {'ss': math.sqrt((n-1)*data2[2]['p']*data2[3]['qq'])}
    if data2[5]['ss'] != 0:
        data2[6] = {'a': (data2[3]['qq']-data2[2]['p'])/data2[5]['ss']}
    else:
        data2[6] = {'a': 0}
    data2[7] = {'Xsup': data2[4]['M'] + get_t(data2[6]['a'], False)*data2[5]['ss']}
    data2[8] = {'Xinf': data2[4]['M'] + get_t(data2[6]['a'], True)*data2[5]['ss']}

    data3 = {}
    data3[1] = {'d': float(sum(ip.values())) / n}
    data3[2] = {'p': float(data3[1]['d']) / (n-1)}
    data3[3] = {'qq': 1 - data3[2]['p']}
    data3[4] = {'M': data3[2]['p'] * (n-1)}
    data3[5] = {'ss': math.sqrt((n-1)*data3[2]['p']*data3[3]['qq'])}
    if data3[5]['ss'] != 0:
        data3[6] = {'a': (data3[3]['qq']-data3[2]['p'])/data3[5]['ss']}
    else:
        data3[6] = {'a': 0}
    data3[7] = {'Xsup': data3[4]['M'] + get_t(data3[6]['a'], False)*data3[5]['ss']}
    data3[8] = {'Xinf': data3[4]['M'] + get_t(data3[6]['a'], True)*data3[5]['ss']}

    data4 = {}
    data4[1] = {'d': float(sum(iN.values())) / n}
    data4[2] = {'p': float(data4[1]['d']) / (n-1)}
    data4[3] = {'qq': 1 - data4[2]['p']}
    data4[4] = {'M': data4[2]['p'] * (n-1)}
    data4[5] = {'ss': math.sqrt((n-1)*data4[2]['p']*data4[3]['qq'])}
    if data4[5]['ss'] != 0:
        data4[6] = {'a': (data4[3]['qq']-data4[2]['p'])/data4[5]['ss']}
    else:
        data4[6] = {'a': 0}
    data4[7] = {'Xsup': data4[4]['M'] + get_t(data4[6]['a'], False)*data4[5]['ss']}
    data4[8] = {'Xinf': data4[4]['M'] + get_t(data4[6]['a'], True)*data4[5]['ss']}
    proposals = get_proposals(sp, np, nn, sn, spval, snval, imp, ipval, imn, inval, iN, ip, ipp, ipval5, ipn, inval6, data1, data2, data3, data4, n, matrix12, matrix34, matrix, '', {}, test.clase.grupo_edad_id)

    return render(request, 'resultados/resultados_grafo.html', {'eva': teacher.evaluacion, 'test': test, 'clase': test.clase.nombre, 'preguntas':preguntas, 'respuestas': json.dumps(matrix), 'ic': proposals['ic'], 'id': proposals['id'],
                                                                'iap': proposals['iap'], 'ian': proposals['ian'], 'alumnos': json.dumps(als), 'sp': json.dumps(sp), 'sn': json.dumps(sn),
                                                                'ip': json.dumps(ip), 'iN': json.dumps(iN), 'recomendaciones': proposals['recomendaciones'], 'alumnosQuery': alumnos, 'year': int(year)})


def show_results_student(request, test, alumno, year):
    pdf = 0
    all = 0
    if 'Pdf' in request.path:
        pdf = 1
    if 'Todos' in request.path:
        all = 1
    studentCurrent = AlumnoTests.objects.get(username=alumno)
    teacherProfile = UserProfile.objects.get(user__username=str(request.user))
    test = Test.objects.get(id=test)
    preguntas = Preguntas_test.objects.filter(test=test)
    alumnos = AlumnoTests.objects.filter(idTest=test)
    als = {}
    for a in alumnos:
        als[a.get_nombre() + " " + a.get_apellidos()] = str(a.username)
    matrix = {}
    matrixText = {}
    for num, pregunta in enumerate(preguntas):
        question = {}
        questionText = {}
        for respuesta in Respuesta.objects.filter(pregunta=pregunta):
            student = AlumnoTests.objects.get(idAl=respuesta.alumno.id, idTest=test)
            j = json.loads(respuesta.respuesta)
            answers = {}
            answersText = {}
            for element in j:
                if 'text' not in element:
                    answers[j.get(element)] = {str('#000000'): str((MIDDLE_POINT - int(element)) + MIDDLE_POINT)}
                    answersText[j.get(element)] = ''
                else:
                    answersText[j.get(element[0])] = j.get(element)
            for e,a in enumerate(alumnos):
                if str(a.username) == str(student.username) or a.username not in answers:
                    answers[a.username] = {str('#000000'): str('')}
            question[student.username] = answers
            questionText[student.username] = answersText
        matrix[num+1] = question
        matrixText[num+1] = questionText
    sp = {}
    spval = {}
    np = {}
    sn = {}
    snval = {}
    nn = {}
    ip = {}
    iN = {}
    ip = {}
    ipval = {}
    imp = {}
    iN = {}
    inval = {}
    imn = {}
    ipp = {}
    ipval5 = {}
    ipn = {}
    inval6 = {}
    matrix12 = {}
    matrix34 = {}
    for m in matrix:
        for answer in matrix[m]:
            if str(answer) not in matrix12:
                matrix12[str(answer)] = {}
            if 'EP' not in matrix12[str(answer)]:
                matrix12[str(answer)]['EP'] = 0
            if 'EN' not in matrix12[str(answer)]:
                matrix12[str(answer)]['EN'] = 0
            if 'RP' not in matrix12[str(answer)]:
                matrix12[str(answer)]['RP'] = 0
            if 'RN' not in matrix12[str(answer)]:
                matrix12[str(answer)]['RN'] = 0
            if str(answer) not in matrix34:
                matrix34[str(answer)] = {}
            if 'PP' not in matrix34[str(answer)]:
                matrix34[str(answer)]['PP'] = 0
            if 'PAP' not in matrix34[str(answer)]:
                matrix34[str(answer)]['PAP'] = 0
            if 'PN' not in matrix34[str(answer)]:
                matrix34[str(answer)]['PN'] = 0
            if 'PAN' not in matrix34[str(answer)]:
                matrix34[str(answer)]['PAN'] = 0
            for student in matrix[m][answer]:
                if student not in sp:
                    sp[student] = 0
                if student not in spval:
                    spval[student] = 0
                if student not in sn:
                    sn[student] = 0
                if student not in snval:
                    snval[student] = 0
                if student not in ip:
                    ip[student] = 0
                if student not in ipval:
                    ipval[student] = 0
                if student not in iN:
                    iN[student] = 0
                if student not in inval:
                    inval[student] = 0
                if student not in ipp:
                    ipp[student] = 0
                if student not in ipn:
                    ipn[student] = 0
                if student not in ipval5:
                    ipval5[student] = 0
                if student not in inval6:
                    inval6[student] = 0
                if matrix[m][answer][student] != {str('#000000'): str('')}:
                    if m == 1:
                        matrix12[str(answer)]['EP'] += 1
                        sp[student] += 1
                        spval[student] += int(matrix[m][answer][student][list(matrix[m][answer][student])[0]])
                        if student in matrix[m]:
                            if matrix[m][student][answer] != {str('#000000'): str('')}:
                                matrix12[str(answer)]['RP'] += 1

                                if '#000000' in matrix[m][answer][student]:
                                    matrix[m][answer][student]['#d6c22b'] = matrix[m][answer][student]['#000000']
                                    del matrix[m][answer][student]['#000000']
                                if '#000000' in matrix[m][student][answer]:
                                    matrix[m][student][answer][str('#d6c22b')] = matrix[m][student][answer]['#000000']
                                    del matrix[m][student][answer]['#000000']
                            if matrix[m + 1][student][answer] != {str('#000000'): str('')}:
                                if '#000000' in matrix[m][answer][student]:
                                    matrix[m][answer][student][str('#e05ab8')] = matrix[m][answer][student]['#000000']
                                    del matrix[m][answer][student]['#000000']
                                if '#000000' in matrix[m+1][student][answer]:
                                    matrix[m+1][student][answer][str('#e05ab8')] = matrix[m+1][student][answer]['#000000']
                                    del matrix[m+1][student][answer]['#000000']
                    elif m == 2:
                        matrix12[str(answer)]['EN'] += 1
                        sn[student] += 1
                        snval[student] += int(matrix[m][answer][student][list(matrix[m][answer][student])[0]])
                        if student in matrix[m]:
                            if matrix[m][student][answer] != {str('#000000'): str('')}:
                                matrix12[str(answer)]['RN'] += 1

                                if '#000000' in matrix[m][answer][student]:
                                    matrix[m][answer][student][str('#0da863')] = matrix[m][answer][student]['#000000']
                                    del matrix[m][answer][student]['#000000']
                                if '#000000' in matrix[m][student][answer]:
                                    matrix[m][student][answer][str('#0da863')] = matrix[m][student][answer]['#000000']
                                    del matrix[m][student][answer]['#000000']
                    elif m == 3:
                        ip[student] += 1
                        ipval[student] += int(matrix[m][answer][student][list(matrix[m][answer][student])[0]])
                        matrix34[str(answer)]['PP'] += 1
                        if student in matrix[m]:
                            if matrix[m-2][student][answer] != {str('#000000'): str('')}:
                                matrix34[str(answer)]['PAP'] += 1
                                if '#000000' in matrix[m][answer][student]:
                                    matrix[m][answer][student][str('#349beb')] = matrix[m][answer][student]['#000000']
                                    del matrix[m][answer][student]['#000000']
                            elif matrix[m-1][student][answer] != {str('#000000'): str('')}:
                                if '#000000' in matrix[m][answer][student]:
                                    matrix[m][answer][student][str('#ed3e46')] = matrix[m][answer][student]['#000000']
                                    del matrix[m][answer][student]['#000000']
                    elif m == 4:
                        iN[student] += 1
                        inval[student] += int(matrix[m][answer][student][list(matrix[m][answer][student])[0]])
                        matrix34[str(answer)]['PN'] += 1
                        if student in matrix[m]:
                            if matrix[m-2][student][answer] != {str('#000000'): str('')}:
                                matrix34[str(answer)]['PAN'] += 1
                                if '#000000' in matrix[m][answer][student]:
                                    matrix[m][answer][student][str('#eb8034')] = matrix[m][answer][student]['#000000']
                                    del matrix[m][answer][student]['#000000']
                            elif matrix[m-3][student][answer] != {str('#000000'): str('')}:
                                if '#000000' in matrix[m][answer][student]:
                                    matrix[m][answer][student][str('#9646e0')] = matrix[m][answer][student]['#000000']
                                    del matrix[m][answer][student]['#000000']
                    elif m == 5:
                        ipval5[student] += int(matrix[m][answer][student][list(matrix[m][answer][student])[0]])
                    elif m == 6:
                        inval6[student] += int(matrix[m][answer][student][list(matrix[m][answer][student])[0]])

    n = len(alumnos)

    for s in spval:
        np[s] = int((float(spval[s]) / ((n - 1) * 5)) * 100)
        nn[s] = int((float(snval[s]) / ((n - 1) * 5)) * 100)
        imp[s] = int((float(ipval[s]) / ((n - 1) * 5)) * 100)
        imn[s] = int((float(inval[s]) / ((n - 1) * 5)) * 100)
        ipp[s] = int((float(ipval5[s]) / ((n - 1) * 5)) * 100)
        ipn[s] = int((float(inval6[s]) / ((n - 1) * 5)) * 100)

    matrix12aux = copy.deepcopy(matrix12)
    matrix34aux = copy.deepcopy(matrix34)
    ic, id, iap, ian = 0, 0, 0, 0
    for m in matrix12:
        for e in matrix12[m]:
            if e == "EP" or e == "EN":
                matrix12[m][e] = int((float(matrix12[m][e]) / MAX_POINTS) * 100)
            elif e == "RP":
                ic += matrix12[m][e]
            elif e == "RN":
                id += matrix12[m][e]
    for m in matrix34:
        for e in matrix34[m]:
            if e == "PAP":
                if matrix34[m]['PP'] != 0:
                    matrix34[m][e] = int((float(matrix34[m][e]) / matrix34[m]['PP']) * 100)
                else:
                    matrix34[m][e] = 0
            elif e == "PAN":
                if matrix34[m]['PN'] != 0:
                    matrix34[m][e] = int((float(matrix34[m][e]) / matrix34[m]['PN']) * 100)
                else:
                    matrix34[m][e] = 0
    for m in matrix34:
        for e in matrix34[m]:
            if e == "PP" or e == "PN":
                matrix34[m][e] = int((float(matrix34[m][e]) / MAX_POINTS) * 100)

    data1 = {}
    data1[1] = {'d': float(sum(sp.values())) / n}
    data1[2] = {'p': float(data1[1]['d']) / (n-1)}
    data1[3] = {'qq': 1 - data1[2]['p']}
    data1[4] = {'M': data1[2]['p'] * (n-1)}
    data1[5] = {'ss': math.sqrt((n-1)*data1[2]['p']*data1[3]['qq'])}
    if data1[5]['ss'] != 0:
        data1[6] = {'a': (data1[3]['qq']-data1[2]['p'])/data1[5]['ss']}
    else:
        data1[6] = {'a': 0}
    data1[7] = {'Xsup': data1[4]['M'] + get_t(data1[6]['a'], False)*data1[5]['ss']}
    data1[8] = {'Xinf': data1[4]['M'] + get_t(data1[6]['a'], True)*data1[5]['ss']}

    data2 = {}
    data2[1] = {'d': float(sum(sn.values())) / n}
    data2[2] = {'p': float(data2[1]['d']) / (n-1)}
    data2[3] = {'qq': 1 - data2[2]['p']}
    data2[4] = {'M': data2[2]['p'] * (n-1)}
    data2[5] = {'ss': math.sqrt((n-1)*data2[2]['p']*data2[3]['qq'])}
    if data2[5]['ss'] != 0:
        data2[6] = {'a': (data2[3]['qq']-data2[2]['p'])/data2[5]['ss']}
    else:
        data2[6] = {'a': 0}
    data2[7] = {'Xsup': data2[4]['M'] + get_t(data2[6]['a'], False)*data2[5]['ss']}
    data2[8] = {'Xinf': data2[4]['M'] + get_t(data2[6]['a'], True)*data2[5]['ss']}

    data3 = {}
    data3[1] = {'d': float(sum(ip.values())) / n}
    data3[2] = {'p': float(data3[1]['d']) / (n-1)}
    data3[3] = {'qq': 1 - data3[2]['p']}
    data3[4] = {'M': data3[2]['p'] * (n-1)}
    data3[5] = {'ss': math.sqrt((n-1)*data3[2]['p']*data3[3]['qq'])}
    if data3[5]['ss'] != 0:
        data3[6] = {'a': (data3[3]['qq']-data3[2]['p'])/data3[5]['ss']}
    else:
        data3[6] = {'a': 0}
    data3[7] = {'Xsup': data3[4]['M'] + get_t(data3[6]['a'], False)*data3[5]['ss']}
    data3[8] = {'Xinf': data3[4]['M'] + get_t(data3[6]['a'], True)*data3[5]['ss']}

    data4 = {}
    data4[1] = {'d': float(sum(iN.values())) / n}
    data4[2] = {'p': float(data4[1]['d']) / (n-1)}
    data4[3] = {'qq': 1 - data4[2]['p']}
    data4[4] = {'M': data4[2]['p'] * (n-1)}
    data4[5] = {'ss': math.sqrt((n-1)*data4[2]['p']*data4[3]['qq'])}
    if data4[5]['ss'] != 0:
        data4[6] = {'a': (data4[3]['qq']-data4[2]['p'])/data4[5]['ss']}
    else:
        data4[6] = {'a': 0}
    data4[7] = {'Xsup': data4[4]['M'] + get_t(data4[6]['a'], False)*data4[5]['ss']}
    data4[8] = {'Xinf': data4[4]['M'] + get_t(data4[6]['a'], True)*data4[5]['ss']}

    proposals = get_proposals(sp, np, nn, sn, spval, snval, imp, ipval, imn, inval, iN, ip, ipp, ipval5, ipn, inval6, data1, data2, data3, data4, n, matrix12aux, matrix34aux, matrix, alumno, matrixText, test.clase.grupo_edad_id)

    pos = get_soc(proposals['sp'][alumno], proposals['sn'][alumno], proposals['ep'][alumno], proposals['en'][alumno], np[alumno], nn[alumno])

    rp = {}
    os = {}
    for al in matrix[1]:
        if al == alumno:
            for st in matrix[1][al]:
                if st in matrix[1]:
                    stOb = AlumnoTests.objects.get(username=st)
                    if "#d6c22b" in matrix[1][al][st] and "#d6c22b" in matrix[1][st][al]:
                        if (int(matrix[1][al][st]['#d6c22b']) == 5 or int(matrix[1][al][st]['#d6c22b'])== 4) and (int(matrix[1][st][al]['#d6c22b']) == 5 or int(matrix[1][st][al]['#d6c22b']) == 4):
                            rp[stOb.idAl] = [ugettext("FUERTE"), matrix[1][al][st]['#d6c22b'], matrix[1][st][al]['#d6c22b']]
                        elif int(matrix[1][al][st]['#d6c22b']) == 3 or int(matrix[1][st][al]['#d6c22b']) == 3 or (int(matrix[1][al][st]['#d6c22b']) == 2 and int(matrix[1][st][al]['#d6c22b']) == 4) or (int(matrix[1][st][al]['#d6c22b']) == 2 and int(matrix[1][al][st]['#d6c22b']) == 4):
                            rp[stOb.idAl] = [ugettext("MEDIA"), matrix[1][al][st]['#d6c22b'], matrix[1][st][al]['#d6c22b']]
                        elif abs(int(matrix[1][al][st]['#d6c22b']) - int(matrix[1][st][al]['#d6c22b'])) >= 2:
                            rp[stOb.idAl] = [ugettext("DESIQUILIBRADA"), matrix[1][al][st]['#d6c22b'], matrix[1][st][al]['#d6c22b']]
                        else:
                            rp[stOb.idAl] = [ugettext("DÉBIL"), matrix[1][al][st]['#d6c22b'], matrix[1][st][al]['#d6c22b']]
                    elif "#e05ab8" in matrix[1][al][st] and "#e05ab8" in matrix[2][st][al]:
                        if (int(matrix[1][al][st]['#e05ab8']) == 5 or int(matrix[1][al][st]['#e05ab8'])== 4) and (int(matrix[2][st][al]['#e05ab8']) == 5 or int(matrix[2][st][al]['#e05ab8']) == 4):
                            os[stOb.idAl] = [ugettext("FUERTE"), matrix[1][al][st]['#e05ab8'], matrix[2][st][al]['#e05ab8'], studentCurrent.idAl, stOb.idAl]
                        elif int(matrix[1][al][st]['#e05ab8']) == 3 or int(matrix[2][st][al]['#e05ab8']) == 3 or (int(matrix[1][al][st]['#e05ab8']) == 2 and int(matrix[2][st][al]['#e05ab8']) == 4) or (int(matrix[2][st][al]['#e05ab8']) == 2 and int(matrix[1][al][st]['#e05ab8']) == 4):
                            os[stOb.idAl] = [ugettext("MEDIA"), matrix[1][al][st]['#e05ab8'], matrix[2][st][al]['#e05ab8'], studentCurrent.idAl, stOb.idAl]
                        elif abs(int(matrix[1][al][st]['#e05ab8']) - int(matrix[2][st][al]['#e05ab8'])) >= 2:
                            os[stOb.idAl] = [ugettext("DESIQUILIBRADA"), matrix[1][al][st]['#e05ab8'], matrix[2][st][al]['#e05ab8'], studentCurrent.idAl, stOb.idAl]
                        else:
                            os[stOb.idAl] = [ugettext("DÉBIL"), matrix[1][al][st]['#e05ab8'], matrix[2][st][al]['#e05ab8'], studentCurrent.idAl, stOb.idAl]

    rn = {}
    for al in matrix[2]:
        if al == alumno:
            for st in matrix[2][al]:
                if st in matrix[2]:
                    stOb = AlumnoTests.objects.get(username=st)
                    if "#0da863" in matrix[2][al][st] and "#0da863" in matrix[2][st][al]:
                        if (int(matrix[2][al][st]['#0da863']) == 5 or int(matrix[2][al][st]['#0da863'])== 4) and (int(matrix[2][st][al]['#0da863']) == 5 or int(matrix[2][st][al]['#0da863']) == 4):
                            rn[stOb.idAl] = [ugettext("FUERTE"), matrix[2][al][st]['#0da863'], matrix[2][st][al]['#0da863']]
                        elif int(matrix[2][al][st]['#0da863']) == 3 or int(matrix[2][st][al]['#0da863']) == 3 or (int(matrix[2][al][st]['#0da863']) == 2 and int(matrix[2][st][al]['#0da863']) == 4) or (int(matrix[2][st][al]['#0da863']) == 2 and int(matrix[2][al][st]['#0da863']) == 4):
                            rn[stOb.idAl] = [ugettext("MEDIA"), matrix[2][al][st]['#0da863'], matrix[2][st][al]['#0da863']]
                        elif abs(int(matrix[2][al][st]['#0da863']) - int(matrix[2][st][al]['#0da863'])) >= 2:
                            rn[stOb.idAl] = [ugettext("DESIQUILIBRADA"), matrix[2][al][st]['#0da863'], matrix[2][st][al]['#0da863']]
                        else:
                            rn[stOb.idAl] = [ugettext("DÉBIL"), matrix[2][al][st]['#0da863'], matrix[2][st][al]['#0da863']]
                    elif "#e05ab8" in matrix[2][al][st] and "#e05ab8" in matrix[1][st][al]:
                        if (int(matrix[2][al][st]['#e05ab8']) == 5 or int(matrix[2][al][st]['#e05ab8'])== 4) and (int(matrix[1][st][al]['#e05ab8']) == 5 or int(matrix[1][st][al]['#e05ab8']) == 4):
                            os[stOb.idAl] = [ugettext("FUERTE"), matrix[1][st][al]['#e05ab8'], matrix[2][al][st]['#e05ab8'], stOb.idAl, studentCurrent.idAl]
                        elif int(matrix[2][al][st]['#e05ab8']) == 3 or int(matrix[1][st][al]['#e05ab8']) == 3 or (int(matrix[2][al][st]['#e05ab8']) == 2 and int(matrix[1][st][al]['#e05ab8']) == 4) or (int(matrix[1][st][al]['#e05ab8']) == 2 and int(matrix[2][al][st]['#e05ab8']) == 4):
                            os[stOb.idAl] = [ugettext("MEDIA"), matrix[1][st][al]['#e05ab8'], matrix[2][al][st]['#e05ab8'], stOb.idAl, studentCurrent.idAl]
                        elif abs(int(matrix[2][al][st]['#e05ab8']) - int(matrix[1][st][al]['#e05ab8'])) >= 2:
                            os[stOb.idAl] = [ugettext("DESIQUILIBRADA"), matrix[1][st][al]['#e05ab8'], matrix[2][al][st]['#e05ab8'], stOb.idAl, studentCurrent.idAl]
                        else:
                            os[stOb.idAl] = [ugettext("DÉBIL"), matrix[1][st][al]['#e05ab8'], matrix[2][al][st]['#e05ab8'], stOb.idAl, studentCurrent.idAl]

    oip = {}
    for al in matrix[3]:
        if al == alumno:
            for st in matrix[3][al]:
                if st in matrix[2]:
                    stOb = AlumnoTests.objects.get(username=st)
                    if "#ed3e46" in matrix[3][al][st] and "#ed3e46" in matrix[2][st][al]:
                        if (int(matrix[3][al][st]['#ed3e46']) == 5 or int(matrix[3][al][st]['#ed3e46'])== 4) and (int(matrix[2][st][al][list(matrix[2][st][al])[0]]) == 5 or int(matrix[2][st][al][list(matrix[2][st][al])[0]]) == 4):
                            oip[stOb.idAl] = [ugettext("FUERTE"), matrix[3][al][st]['#ed3e46'], matrix[2][st][al][list(matrix[2][st][al])[0]]]
                        elif int(matrix[3][al][st]['#ed3e46']) == 3 or int(matrix[2][st][al][list(matrix[2][st][al])[0]]) == 3 or (int(matrix[3][al][st]['#ed3e46']) == 2 and int(matrix[2][st][al][list(matrix[2][st][al])[0]]) == 4) or (int(matrix[2][st][al][list(matrix[2][st][al])[0]]) == 2 and int(matrix[3][al][st]['#ed3e46']) == 4):
                            oip[stOb.idAl] = [ugettext("MEDIA"), matrix[3][al][st]['#ed3e46'], matrix[2][st][al][list(matrix[2][st][al])[0]]]
                        elif abs(int(matrix[3][al][st]['#ed3e46']) - int(matrix[2][st][al][list(matrix[2][st][al])[0]])) >= 2:
                            oip[stOb.idAl] = [ugettext("DESIQUILIBRADA"), matrix[3][al][st]['#ed3e46'], matrix[2][st][al][list(matrix[2][st][al])[0]]]
                        else:
                            oip[stOb.idAl] = [ugettext("DÉBIL"), matrix[3][al][st]['#ed3e46'], matrix[2][st][al][list(matrix[2][st][al])[0]]]

    oin = {}
    for al in matrix[4]:
        if al == alumno:
            for st in matrix[4][al]:
                if st in matrix[1]:
                    stOb = AlumnoTests.objects.get(username=st)
                    if "#9646e0" in matrix[4][al][st] and "#9646e0" in matrix[1][st][al]:
                        if (int(matrix[4][al][st]['#9646e0']) == 5 or int(matrix[4][al][st]['#9646e0'])== 4) and (int(matrix[1][st][al][list(matrix[1][st][al])[0]]) == 5 or int(matrix[1][st][al][list(matrix[1][st][al])[0]]) == 4):
                            oin[stOb.idAl] = [ugettext("FUERTE"), matrix[1][st][al][list(matrix[1][st][al])[0]], matrix[4][al][st]['#9646e0']]
                        elif int(matrix[4][al][st]['#9646e0']) == 3 or int(matrix[1][st][al][list(matrix[1][st][al])[0]]) == 3 or (int(matrix[4][al][st]['#9646e0']) == 2 and int(matrix[1][st][al][list(matrix[1][st][al])[0]]) == 4) or (int(matrix[1][st][al][list(matrix[1][st][al])[0]]) == 2 and int(matrix[4][al][st]['#9646e0']) == 4):
                            oin[stOb.idAl] = [ugettext("MEDIA"), matrix[1][st][al][list(matrix[1][st][al])[0]], matrix[4][al][st]['#9646e0']]
                        elif abs(int(matrix[4][al][st]['#9646e0']) - int(matrix[1][st][al][list(matrix[1][st][al])[0]])) >= 2:
                            oin[stOb.idAl] = [ugettext("DESIQUILIBRADA"), matrix[1][st][al][list(matrix[1][st][al])[0]], matrix[4][al][st]['#9646e0']]
                        else:
                            oin[stOb.idAl] = [ugettext("DÉBIL"), matrix[1][st][al][list(matrix[1][st][al])[0]], matrix[4][al][st]['#9646e0']]

    if pdf == 1:
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachement; filename="Informe-Completo-Alumno-{0}-Cuestionario-{1}.pdf"'.format(studentCurrent.idAl.nombre + " " + studentCurrent.idAl.apellidos, test.nombre)

        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=100, bottomMargin=50)
        doc.pagesize = portrait(A4)
        elements = []

        #Configure style and word wrap
        s = getSampleStyleSheet()
        s = s['BodyText']
        s.wordWrap = 'CJK'
        s.fontName = 'Helvetica'
        s.alignment = 1
        s.fontSize = 20
        title = Paragraph(ugettext("Informe de {0} {1}".format(studentCurrent.idAl.nombre, studentCurrent.idAl.apellidos)), s)
        elements.append(title)
        s.fontSize = 10

        sLeft = getSampleStyleSheet()
        sLeft = sLeft['BodyText']
        sLeft.wordWrap = 'CJK'
        sLeft.fontName = 'Helvetica'
        sLeft.alignment = 0
        sLeft.fontSize = 10

        style = [
            ('LINEBELOW', (0, 0), (-1, -2), 0.25, colors.gray),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
            ('LINEABOVE', (0,0), (-1,0), 1, colors.gray)
        ]

        data = []
        aux = []

        aux.append(ugettext("Alias"))
        if studentCurrent.idAl.alias:
            aux.append(studentCurrent.idAl.alias)
        else:
            aux.append('')
        data.append(aux)
        aux = []
        aux.append(ugettext("DNI"))
        if studentCurrent.idAl.DNI:
            aux.append(studentCurrent.idAl.DNI)
        else:
            aux.append('')
        data.append(aux)
        aux = []
        aux.append(ugettext("Fecha de nacimiento"))
        aux.append(studentCurrent.idAl.fecha_nacimiento.strftime('%d/%m/%Y'))
        data.append(aux)
        aux = []
        aux.append(ugettext("Sexo"))
        aux.append(studentCurrent.idAl.get_sexo_display())
        data.append(aux)
        aux = []
        aux.append(ugettext("Clase"))
        aux.append(test.clase.nombre)
        data.append(aux)
        aux = []
        aux.append(ugettext("Tutor responsable"))
        aux.append(teacherProfile.nombre + " " + teacherProfile.apellidos)
        data.append(aux)
        aux = []
        aux.append(ugettext("Nombre del test"))
        aux.append(test.nombre)
        data.append(aux)
        aux = []
        aux.append(ugettext("Fecha de creación del test"))
        aux.append(str(test.date_created.strftime('%d/%m/%Y %H:%M')))
        data.append(aux)
        dataAux = []
        for r, row in enumerate(data):
            aux = []
            for c, cell in enumerate(row):
                if c == 0 and (0 <= r <= len(data) - 1):
                    sLeft.fontName = 'Helvetica-Oblique'
                else:
                    sLeft.fontName = 'Helvetica'
                sLeft.fontSize = 9
                aux.append(Paragraph(cell, sLeft))
            dataAux.append(aux)
        t=Table(dataAux, spaceAfter=50, spaceBefore=50)
        t.setStyle(TableStyle(style))

        elements.append(t)

        s.fontName = 'Helvetica-Bold'
        s.fontSize = 14
        elements.append(Paragraph(ugettext("Resultados de las preguntas"),s))
        s.fontName = 'Helvetica'
        s.fontSize = 9
        elements.append(Spacer(1, 0.25*inch))

        style = [
            ('LINEBELOW', (0, 1), (-1, -1), 0.25, colors.gray),
            ('LINEBELOW', (0, 0), (-1, 0), 1, colors.gray),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
            ('LINEABOVE', (0,0), (-1,0), 1, colors.white),
            ('LINEBEFORE', (1, 1), (-1, 1), 0.25, colors.gray),
            ('LINEBEFORE', (1, -1), (-1, -1), 0.25, colors.gray)
        ]


        for num in matrix:
            data = []
            aux = []
            s.fontSize = 12
            elements.append(Paragraph(ugettext("Pregunta") + " #" + str(num) + ".- " + return_tipo_pregunta(preguntas, num) + " (" + ugettext("Tipo") + " " + str(num) + ") ",s))
            s.fontSize = 9
            elements.append(Spacer(1, 0.15*inch))
            elements.append(Paragraph(return_pregunta(preguntas, num),s))
            aux.append("1º")
            aux.append("2º")
            aux.append("3º")
            aux.append("4º")
            aux.append("5º")
            data.append(aux)
            aux = []
            for user in matrix[num]:
                if user == studentCurrent.username:
                    aux.append(return_value(matrix[num][user], 5))
                    aux.append(return_value(matrix[num][user], 4))
                    aux.append(return_value(matrix[num][user], 3))
                    aux.append(return_value(matrix[num][user], 2))
                    aux.append(return_value(matrix[num][user], 1))
                    data.append(aux)
                    aux = []
                    if num == 2 or num == 4 or num == 6:
                        aux.append(ugettext('¿Por qué?'))
                        data.append(aux)
                        aux = []
                        for userText in matrixText[num][studentCurrent.username]:
                            if userText == return_text(matrix[num][user], 5):
                                aux.append(matrixText[num][studentCurrent.username][userText])
                        for userText in matrixText[num][studentCurrent.username]:
                            if userText == return_text(matrix[num][user], 4):
                                aux.append(matrixText[num][studentCurrent.username][userText])
                        for userText in matrixText[num][studentCurrent.username]:
                            if userText == return_text(matrix[num][user], 3):
                                aux.append(matrixText[num][studentCurrent.username][userText])
                        for userText in matrixText[num][studentCurrent.username]:
                            if userText == return_text(matrix[num][user], 2):
                                aux.append(matrixText[num][studentCurrent.username][userText])
                        for userText in matrixText[num][studentCurrent.username]:
                            if userText == return_text(matrix[num][user], 1):
                                aux.append(matrixText[num][studentCurrent.username][userText])
                        data.append(aux)
                        aux = []

            dataAux = []
            for r, row in enumerate(data):
                aux = []
                for c, cell in enumerate(row):
                    if ((0 <= c <= len(row) -1) and r == 0) or r == 2:
                        sLeft.fontName = 'Helvetica-Bold'
                    else:
                        sLeft.fontName = 'Helvetica'
                    sLeft.fontSize = 9
                    aux.append(Paragraph(cell, sLeft))
                dataAux.append(aux)
            t=Table(dataAux, spaceAfter=50, spaceBefore=20)
            t.setStyle(TableStyle(style))

            elements.append(t)

        elements.append(PageBreak())
        doc.pagesize = landscape(A4)

        s.fontName = 'Helvetica-Bold'
        s.fontSize = 14
        elements.append(Paragraph(ugettext("Análisis de resultados"),s))
        s.fontName = 'Helvetica'
        s.fontSize = 9
        elements.append(Spacer(1, 0.25*inch))

        s.fontSize = 12
        elements.append(Paragraph(ugettext("1.- POSICIÓN SOCIOMÉTRICA (SP, SN, EP Y EN)"),s))
        s.fontSize = 9

        style = [
            ('LINEBELOW', (0, 1), (-1, -1), 0.25, colors.gray),
            ('LINEBELOW', (0, 0), (-1, 0), 1, colors.gray),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
            ('LINEABOVE', (0,0), (-1,0), 1, colors.white),
            ('LINEBEFORE', (1, 1), (-1, 1), 0.25, colors.gray),
            ('LINEBEFORE', (1, -1), (-1, -1), 0.25, colors.gray)
        ]

        data = []
        aux = []

        aux.append("SP")
        aux.append("SN")
        aux.append("EP")
        aux.append("EN")
        data.append(aux)
        aux = []
        aux.append(str(sp[alumno]))
        aux.append(str(sn[alumno]))
        aux.append(str(matrix12[str(alumno)]['EP']) + "%")
        aux.append(str(matrix12[str(alumno)]['EN']) + "%")
        data.append(aux)

        aux = []
        dataAux = []
        for r, row in enumerate(data):
            aux = []
            for c, cell in enumerate(row):
                if r == 0:
                    sLeft.fontName = 'Helvetica-Bold'
                    sLeft.textColor = 'black'
                else:
                    sLeft.fontName = 'Helvetica'
                    if c == 0:
                        if proposals['sp'][alumno][list(proposals['sp'][alumno])[0]] == gettext("Bajo"):
                            sLeft.textColor = 'red'
                        else:
                            sLeft.textColor = 'black'
                    elif c == 1:
                        if proposals['sn'][alumno][list(proposals['sn'][alumno])[0]] == gettext("Alto"):
                            sLeft.textColor = 'red'
                        else:
                            sLeft.textColor = 'black'
                    elif c == 2:
                        percent = int(cell[0:-1])
                        if percent <= 25:
                            sLeft.textColor = 'red'
                        else:
                            sLeft.textColor = 'black'
                    else:
                        percent = int(cell[0:-1])
                        if percent >= 75:
                            sLeft.textColor = 'red'
                        else:
                            sLeft.textColor = 'black'
                sLeft.fontSize = 9



                aux.append(Paragraph(cell, sLeft))
            dataAux.append(aux)
        t=Table(dataAux, spaceAfter=50, spaceBefore=30)
        t.setStyle(TableStyle(style))


        elements.append(t)

        data = []
        aux = []
        aux.append(ugettext("POSICIÓN SOC"))
        data.append(aux)
        aux = []
        aux.append(pos)
        data.append(aux)
        aux = []
        dataAux = []
        for r, row in enumerate(data):
            aux = []
            for c, cell in enumerate(row):
                sLeft.fontName = 'Helvetica-Bold'
                sLeft.fontSize = 9
                aux.append(Paragraph(cell, sLeft))
            dataAux.append(aux)
        t=Table(dataAux, spaceAfter=50, spaceBefore=30)
        t.setStyle(TableStyle(style))

        elements.append(t)

        s.fontSize = 12
        elements.append(Paragraph(ugettext("2.- ESTATUS POSITIVO (SP) Y NIVEL MEDIO DE POPULARIDAD (NP)"),s))
        s.fontSize = 9

        data = []
        aux = []

        aux.append(ugettext("NIVEL SP"))
        aux.append(ugettext("VALOR NP"))
        data.append(aux)
        aux = []
        aux.append(str(proposals['sp'][alumno][list(proposals['sp'][alumno])[0]]))
        aux.append(str(np[alumno]) + "%")
        data.append(aux)
        aux = []
        dataAux = []
        for r, row in enumerate(data):
            aux = []
            for c, cell in enumerate(row):
                if r == 0:
                    sLeft.fontName = 'Helvetica-Bold'
                    sLeft.textColor = 'black'
                else:
                    sLeft.fontName = 'Helvetica'
                    if c == 0:
                        if proposals['sp'][alumno][list(proposals['sp'][alumno])[0]] == gettext("Bajo"):
                            sLeft.textColor = 'red'
                        else:
                            sLeft.textColor = 'black'
                    else:
                        percent = int(cell[0:-1])
                        if percent <= 25:
                            sLeft.textColor = 'red'
                        else:
                            sLeft.textColor = 'black'
                sLeft.fontSize = 9
                aux.append(Paragraph(cell, sLeft))
            dataAux.append(aux)
        t=Table(dataAux, spaceAfter=50, spaceBefore=30)
        t.setStyle(TableStyle(style))

        elements.append(t)

        s.fontSize = 12
        elements.append(Paragraph(ugettext("3.- ESTATUS NEGATIVO (SN) Y NIVEL MEDIO DE RECHAZO (NN)"),s))
        s.fontSize = 9

        data = []
        aux = []

        aux.append(ugettext("NIVEL SN"))
        aux.append(ugettext("VALOR NN"))
        data.append(aux)
        aux = []
        aux.append(str(proposals['sn'][alumno][list(proposals['sn'][alumno])[0]]))
        aux.append(str(nn[alumno]) + "%")
        data.append(aux)
        aux = []
        dataAux = []
        for r, row in enumerate(data):
            aux = []
            for c, cell in enumerate(row):
                if r == 0:
                    sLeft.fontName = 'Helvetica-Bold'
                    sLeft.textColor = 'black'
                else:
                    sLeft.fontName = 'Helvetica'
                    if c == 0:
                        if proposals['sn'][alumno][list(proposals['sn'][alumno])[0]] == gettext("Alto"):
                            sLeft.textColor = 'red'
                        else:
                            sLeft.textColor = 'black'
                    else:
                        percent = int(cell[0:-1])
                        if percent >= 75:
                            sLeft.textColor = 'red'
                        else:
                            sLeft.textColor = 'black'
                sLeft.fontSize = 9
                aux.append(Paragraph(cell, sLeft))
            dataAux.append(aux)
        t=Table(dataAux, spaceAfter=50, spaceBefore=30)
        t.setStyle(TableStyle(style))

        elements.append(t)

        s.fontSize = 12
        elements.append(Paragraph(ugettext("4.- AMISTADES (RP)"),s))
        s.fontSize = 9

        data = []
        aux = []

        aux.append(ugettext("NOMBRE"))
        aux.append(ugettext("GRADO"))
        data.append(aux)
        aux = []
        for amigo in rp:
            aux.append(amigo.nombre + " " + amigo.apellidos)
            aux.append(str(rp[amigo][1]) + "-" + str(rp[amigo][2]))
            aux.append(rp[amigo][0])
            data.append(aux)
            aux = []

        if len(rp) == 0:
            aux.append(str(ugettext("No hay")))
            data.append(aux)

        dataAux = []
        for r, row in enumerate(data):
            aux = []
            for c, cell in enumerate(row):
                if r == 0:
                    sLeft.fontName = 'Helvetica-Bold'
                    sLeft.textColor = 'black'
                else:
                    sLeft.fontName = 'Helvetica'
                    if cell == str(ugettext("No hay")):
                        sLeft.textColor = 'red'
                sLeft.fontSize = 9
                aux.append(Paragraph(cell, sLeft))
            dataAux.append(aux)
        t=Table(dataAux, spaceAfter=50, spaceBefore=30)
        t.setStyle(TableStyle(style))
        elements.append(t)

        s.fontSize = 12
        elements.append(Paragraph(ugettext("5.- ENEMISTADES (RN)"),s))
        s.fontSize = 9

        data = []
        aux = []

        aux.append(ugettext("NOMBRE"))
        aux.append(ugettext("GRADO"))
        data.append(aux)
        aux = []
        for amigo in rn:
            aux.append(amigo.nombre + " " + amigo.apellidos)
            aux.append(str(rn[amigo][1]) + "-" + str(rn[amigo][2]))
            aux.append(rn[amigo][0])
            data.append(aux)
            aux = []

        if len(rn) == 0:
            aux.append(str(ugettext("No hay")))
            data.append(aux)

        dataAux = []
        for r, row in enumerate(data):
            aux = []
            for c, cell in enumerate(row):
                if r == 0:
                    sLeft.fontName = 'Helvetica-Bold'
                    sLeft.textColor = 'black'
                else:
                    sLeft.fontName = 'Helvetica'
                sLeft.fontSize = 9
                aux.append(Paragraph(cell, sLeft))
            dataAux.append(aux)
        t=Table(dataAux, spaceAfter=50, spaceBefore=30)
        t.setStyle(TableStyle(style))
        elements.append(t)

        s.fontSize = 12
        elements.append(Paragraph(ugettext("6.- OPOSICIÓN DE SENTIMIENTO (OS)"),s))
        s.fontSize = 9

        data = []
        aux = []

        aux.append(ugettext("ELIGE"))
        aux.append(ugettext("RECHAZA"))
        aux.append(ugettext("GRADO"))
        data.append(aux)
        aux = []
        for amigo in os:
            aux.append(os[amigo][3].nombre + " " + os[amigo][3].apellidos)
            aux.append(os[amigo][4].nombre + " " + os[amigo][4].apellidos)
            aux.append(str(os[amigo][1]) + "-" + str(os[amigo][2]))
            aux.append(os[amigo][0])
            data.append(aux)
            aux = []

        if len(os) == 0:
            aux.append(str(ugettext("No hay")))
            data.append(aux)

        dataAux = []
        for r, row in enumerate(data):
            aux = []
            for c, cell in enumerate(row):
                if r == 0:
                    sLeft.fontName = 'Helvetica-Bold'
                    sLeft.textColor = 'black'
                else:
                    sLeft.fontName = 'Helvetica'
                sLeft.fontSize = 9
                aux.append(Paragraph(cell, sLeft))
            dataAux.append(aux)
        t=Table(dataAux, spaceAfter=50, spaceBefore=30)
        t.setStyle(TableStyle(style))
        elements.append(t)

        s.fontSize = 12
        elements.append(Paragraph(ugettext("7.- GRADO DE SOCIABILIDAD O EXPANSIVIDAD (EP)"),s))
        s.fontSize = 9
        data = []
        aux = []

        aux.append(ugettext("VALOR EP"))
        aux.append(ugettext("NIVEL EP"))
        data.append(aux)
        aux = []
        aux.append(str(matrix12[str(alumno)]['EP']) + "%")
        aux.append(str(proposals['ep'][alumno][list(proposals['ep'][alumno])[0]]))
        data.append(aux)
        aux = []
        dataAux = []
        for r, row in enumerate(data):
            aux = []
            for c, cell in enumerate(row):
                if r == 0:
                    sLeft.fontName = 'Helvetica-Bold'
                    sLeft.textColor = 'black'
                else:
                    sLeft.fontName = 'Helvetica'
                    if c == 1:
                        if proposals['ep'][alumno][list(proposals['ep'][alumno])[0]] == gettext("Bajo"):
                            sLeft.textColor = 'red'
                        else:
                            sLeft.textColor = 'black'
                    else:
                        percent = int(cell[0:-1])
                        if percent <= 25:
                            sLeft.textColor = 'red'
                        else:
                            sLeft.textColor = 'black'
                sLeft.fontSize = 9
                aux.append(Paragraph(cell, sLeft))
            dataAux.append(aux)
        t=Table(dataAux, spaceAfter=50, spaceBefore=30)
        t.setStyle(TableStyle(style))

        elements.append(t)

        s.fontSize = 12
        elements.append(Paragraph(ugettext("8.- EXPECTATIVA DE SER ELEGIDO (PP)"),s))
        s.fontSize = 9

        data = []
        aux = []

        aux.append(ugettext("VALOR PP"))
        aux.append(ugettext("NIVEL PP"))
        data.append(aux)
        aux = []
        aux.append(str(matrix34[str(alumno)]['PP']) + "%")
        aux.append(str(proposals['pp'][alumno][list(proposals['pp'][alumno])[0]]))
        data.append(aux)
        aux = []
        dataAux = []
        for r, row in enumerate(data):
            aux = []
            for c, cell in enumerate(row):
                if r == 0:
                    sLeft.fontName = 'Helvetica-Bold'
                    sLeft.textColor = 'black'
                else:
                    sLeft.fontName = 'Helvetica'
                    if c == 1:
                        if proposals['pp'][alumno][list(proposals['pp'][alumno])[0]] == gettext("Bajo"):
                            sLeft.textColor = 'red'
                        else:
                            sLeft.textColor = 'black'
                    else:
                        percent = int(cell[0:-1])
                        if percent <= 25:
                            sLeft.textColor = 'red'
                        else:
                            sLeft.textColor = 'black'
                sLeft.fontSize = 9
                aux.append(Paragraph(cell, sLeft))
            dataAux.append(aux)
        t=Table(dataAux, spaceAfter=50, spaceBefore=30)
        t.setStyle(TableStyle(style))

        elements.append(t)

        s.fontSize = 12
        elements.append(Paragraph(ugettext("9.- GRADO DE ACIERTO EN LA EXPECTATIVA DE SER ELEGIDO (PAP)"),s))
        s.fontSize = 9

        data = []
        aux = []

        aux.append(ugettext("VALOR PAP"))
        aux.append(ugettext("NIVEL PAP"))
        data.append(aux)
        aux = []
        aux.append(str(matrix34[str(alumno)]['PAP']) + "%")
        aux.append(str(proposals['pap'][alumno][list(proposals['pap'][alumno])[0]]))
        data.append(aux)
        aux = []
        dataAux = []
        for r, row in enumerate(data):
            aux = []
            for c, cell in enumerate(row):
                if r == 0:
                    sLeft.fontName = 'Helvetica-Bold'
                    sLeft.textColor = 'black'
                else:
                    sLeft.fontName = 'Helvetica'
                sLeft.fontSize = 9
                aux.append(Paragraph(cell, sLeft))
            dataAux.append(aux)
        t=Table(dataAux, spaceAfter=50, spaceBefore=30)
        t.setStyle(TableStyle(style))
        elements.append(t)

        s.fontSize = 12
        elements.append(Paragraph(ugettext("10.- OPOSICIÓN ENTRE LA EXPECTATIVA DE SER ELEGIDO Y LA REALIDAD DE SER RECHAZADO (OIP)"),s))
        s.fontSize = 9

        data = []
        aux = []

        aux.append(ugettext("NOMBRE"))
        aux.append(ugettext("GRADO"))
        data.append(aux)
        aux = []
        for amigo in oip:
            aux.append(amigo.nombre + " " + amigo.apellidos)
            aux.append(str(oip[amigo][1]) + "-" + str(oip[amigo][2]))
            aux.append(oip[amigo][0])
            data.append(aux)
            aux = []

        if len(oip) == 0:
            aux.append(str(ugettext("No hay")))
            data.append(aux)

        dataAux = []
        for r, row in enumerate(data):
            aux = []
            for c, cell in enumerate(row):
                if r == 0:
                    sLeft.fontName = 'Helvetica-Bold'
                    sLeft.textColor = 'black'
                else:
                    sLeft.fontName = 'Helvetica'
                sLeft.fontSize = 9
                aux.append(Paragraph(cell, sLeft))
            dataAux.append(aux)
        t=Table(dataAux, spaceAfter=50, spaceBefore=30)
        t.setStyle(TableStyle(style))
        elements.append(t)

        s.fontSize = 12
        elements.append(Paragraph(ugettext("11.- GRADO DE ANTIPATÍA (EN)"),s))
        s.fontSize = 9

        data = []
        aux = []

        aux.append(ugettext("VALOR EN"))
        aux.append(ugettext("NIVEL EN"))
        data.append(aux)
        aux = []
        aux.append(str(matrix12[str(alumno)]['EN']) + "%")
        aux.append(str(proposals['en'][alumno][list(proposals['en'][alumno])[0]]))
        data.append(aux)
        aux = []
        dataAux = []
        for r, row in enumerate(data):
            aux = []
            for c, cell in enumerate(row):
                if r == 0:
                    sLeft.fontName = 'Helvetica-Bold'
                    sLeft.textColor = 'black'
                else:
                    sLeft.fontName = 'Helvetica'
                    if c == 1:
                        if proposals['en'][alumno][list(proposals['en'][alumno])[0]] == gettext("Alto"):
                            sLeft.textColor = 'red'
                        else:
                            sLeft.textColor = 'black'
                    else:
                        percent = int(cell[0:-1])
                        if percent >= 75:
                            sLeft.textColor = 'red'
                        else:
                            sLeft.textColor = 'black'
                sLeft.fontSize = 9
                aux.append(Paragraph(cell, sLeft))
            dataAux.append(aux)
        t=Table(dataAux, spaceAfter=50, spaceBefore=30)
        t.setStyle(TableStyle(style))
        elements.append(t)

        s.fontSize = 12
        elements.append(Paragraph(ugettext("12.- EXPECTATIVA DE SER RECHAZADO (PN)"),s))
        s.fontSize = 9

        data = []
        aux = []

        aux.append(ugettext("VALOR PN"))
        aux.append(ugettext("NIVEL PN"))
        data.append(aux)
        aux = []
        aux.append(str(matrix34[str(alumno)]['PN']) + "%")
        aux.append(str(proposals['pn'][alumno][list(proposals['pn'][alumno])[0]]))
        data.append(aux)
        aux = []
        dataAux = []
        for r, row in enumerate(data):
            aux = []
            for c, cell in enumerate(row):
                if r == 0:
                    sLeft.fontName = 'Helvetica-Bold'
                    sLeft.textColor = 'black'
                else:
                    sLeft.fontName = 'Helvetica'
                    if c == 1:
                        if proposals['pn'][alumno][list(proposals['pn'][alumno])[0]] == gettext("Alto"):
                            sLeft.textColor = 'red'
                        else:
                            sLeft.textColor = 'black'
                    else:
                        percent = int(cell[0:-1])
                        if percent >= 75:
                            sLeft.textColor = 'red'
                        else:
                            sLeft.textColor = 'black'
                sLeft.fontSize = 9
                aux.append(Paragraph(cell, sLeft))
            dataAux.append(aux)
        t=Table(dataAux, spaceAfter=50, spaceBefore=30)
        t.setStyle(TableStyle(style))
        elements.append(t)

        s.fontSize = 12
        elements.append(Paragraph(ugettext("13.- GRADO DE ACIERTO EN LA EXPECTATIVA DE SER RECHAZADO (PAN)"),s))
        s.fontSize = 9

        data = []
        aux = []

        aux.append(ugettext("VALOR PAN"))
        aux.append(ugettext("NIVEL PAN"))
        data.append(aux)
        aux = []
        aux.append(str(matrix34[str(alumno)]['PAN']) + "%")
        aux.append(str(proposals['pan'][alumno][list(proposals['pan'][alumno])[0]]))
        data.append(aux)
        aux = []
        dataAux = []
        for r, row in enumerate(data):
            aux = []
            for c, cell in enumerate(row):
                if r == 0:
                    sLeft.fontName = 'Helvetica-Bold'
                    sLeft.textColor = 'black'
                else:
                    sLeft.fontName = 'Helvetica'
                sLeft.fontSize = 9
                aux.append(Paragraph(cell, sLeft))
            dataAux.append(aux)
        t=Table(dataAux, spaceAfter=50, spaceBefore=30)
        t.setStyle(TableStyle(style))
        elements.append(t)

        s.fontSize = 12
        elements.append(Paragraph(ugettext("14.- OPOSICIÓN ENTRE LA EXPECTATIVA DE SER RECHAZADO A LA REALIDAD DE SER ELEGIDO (OIN)"),s))
        s.fontSize = 9

        data = []
        aux = []


        aux.append(ugettext("NOMBRE"))
        aux.append(ugettext("GRADO"))
        data.append(aux)
        aux = []
        for amigo in oin:
            aux.append(amigo.nombre + " " + amigo.apellidos)
            aux.append(str(oin[amigo][1]) + "-" + str(oin[amigo][2]))
            aux.append(oin[amigo][0])
            data.append(aux)
            aux = []

        if len(oin) == 0:
            aux.append(str(ugettext("No hay")))
            data.append(aux)

        dataAux = []
        for r, row in enumerate(data):
            aux = []
            for c, cell in enumerate(row):
                if r == 0:
                    sLeft.fontName = 'Helvetica-Bold'
                else:
                    sLeft.fontName = 'Helvetica'
                sLeft.fontSize = 9
                aux.append(Paragraph(cell, sLeft))
            dataAux.append(aux)
        t=Table(dataAux, spaceAfter=50, spaceBefore=30)
        t.setStyle(TableStyle(style))
        elements.append(t)

        s.fontSize = 12
        elements.append(Paragraph(ugettext("15.- IMPRESIÓN QUE TIENE EL GRUPO DE SER ELEGIDO POR EL/ELLA (IP E IMP)"),s))
        s.fontSize = 9

        data = []
        aux = []

        aux.append(ugettext("VALOR IP"))
        aux.append(ugettext("NIVEL IP"))
        aux.append(ugettext("VALOR IMP"))
        aux.append(ugettext("NIVEL IMP"))
        data.append(aux)
        aux = []
        aux.append(str(ip[alumno]))
        aux.append(str(proposals['ip'][alumno][list(proposals['ip'][alumno])[0]]))
        aux.append(str(imp[alumno]) + "%")
        aux.append(str(proposals['imp'][alumno][list(proposals['imp'][alumno])[0]]))
        data.append(aux)
        aux = []
        dataAux = []
        for r, row in enumerate(data):
            aux = []
            for c, cell in enumerate(row):
                if r == 0:
                    sLeft.fontName = 'Helvetica-Bold'
                else:
                    sLeft.fontName = 'Helvetica'
                    if c == 1:
                        if proposals['ip'][alumno][list(proposals['ip'][alumno])[0]] == gettext("Bajo"):
                            sLeft.textColor = 'red'
                        else:
                            sLeft.textColor = 'black'
                    elif c == 3:
                        if proposals['imp'][alumno][list(proposals['imp'][alumno])[0]] == gettext("Alto"):
                            sLeft.textColor = 'red'
                        else:
                            sLeft.textColor = 'black'
                    elif c == 0:
                        if proposals['ip'][alumno][list(proposals['ip'][alumno])[0]] == gettext("Bajo"):
                            sLeft.textColor = 'red'
                        else:
                            sLeft.textColor = 'black'
                    else:
                        percent = int(cell[0:-1])
                        if percent >= 75:
                            sLeft.textColor = 'red'
                        else:
                            sLeft.textColor = 'black'
                sLeft.fontSize = 9
                aux.append(Paragraph(cell, sLeft))
            dataAux.append(aux)
        t=Table(dataAux, spaceAfter=50, spaceBefore=30)
        t.setStyle(TableStyle(style))
        elements.append(t)

        s.fontSize = 12
        elements.append(Paragraph(ugettext("16.- IMPRESIÓN QUE TIENE EL GRUPO DE SER RECHAZADO POR EL/ELLA (IN E IMN)"),s))
        s.fontSize = 9

        data = []
        aux = []

        aux.append(ugettext("VALOR IN"))
        aux.append(ugettext("NIVEL IN"))
        aux.append(ugettext("VALOR IMN"))
        aux.append(ugettext("NIVEL IMN"))
        data.append(aux)
        aux = []
        aux.append(str(iN[alumno]))
        aux.append(str(proposals['in'][alumno][list(proposals['in'][alumno])[0]]))
        aux.append(str(imn[alumno]) + "%")
        aux.append(str(proposals['imn'][alumno][list(proposals['imn'][alumno])[0]]))
        data.append(aux)
        aux = []
        dataAux = []
        for r, row in enumerate(data):
            aux = []
            for c, cell in enumerate(row):
                if r == 0:
                    sLeft.fontName = 'Helvetica-Bold'
                    sLeft.textColor = 'black'
                else:
                    sLeft.fontName = 'Helvetica'
                    if c == 1:
                        if proposals['in'][alumno][list(proposals['in'][alumno])[0]] == gettext("Alto"):
                            sLeft.textColor = 'red'
                        else:
                            sLeft.textColor = 'black'
                    elif c == 3:
                        if proposals['imn'][alumno][list(proposals['imn'][alumno])[0]] == gettext("Alto"):
                            sLeft.textColor = 'red'
                        else:
                            sLeft.textColor = 'black'
                    elif c == 0:
                        if proposals['in'][alumno][list(proposals['in'][alumno])[0]] == gettext("Alto"):
                            sLeft.textColor = 'red'
                        else:
                            sLeft.textColor = 'black'
                    else:
                        percent = int(cell[0:-1])
                        if percent >= 75:
                            sLeft.textColor = 'red'
                        else:
                            sLeft.textColor = 'black'
                sLeft.fontSize = 9
                aux.append(Paragraph(cell, sLeft))
            dataAux.append(aux)
        t=Table(dataAux, spaceAfter=50, spaceBefore=30)
        t.setStyle(TableStyle(style))
        elements.append(t)

        s.fontSize = 12
        elements.append(Paragraph(ugettext("17.- NIVEL DE PREFERENCIA SOCIAL POSITIVA (IPP): LÍDER"),s))
        s.fontSize = 9

        data = []
        aux = []

        aux.append(ugettext("VALOR IPP"))
        aux.append(ugettext("NIVEL IPP"))
        data.append(aux)
        aux = []
        aux.append(str(ipp[alumno]) + "%")
        aux.append(str(proposals['ipp'][alumno][list(proposals['ipp'][alumno])[0]]))
        data.append(aux)
        aux = []
        dataAux = []
        for r, row in enumerate(data):
            aux = []
            for c, cell in enumerate(row):
                if r == 0:
                    sLeft.fontName = 'Helvetica-Bold'
                    sLeft.textColor = 'black'
                else:
                    sLeft.fontName = 'Helvetica'
                    if c == 1:
                        if proposals['ipp'][alumno][list(proposals['ipp'][alumno])[0]] == gettext("Alto"):
                            sLeft.textColor = 'red'
                        else:
                            sLeft.textColor = 'black'
                    else:
                        percent = int(cell[0:-1])
                        if percent >= 75:
                            sLeft.textColor = 'red'
                        else:
                            sLeft.textColor = 'black'
                sLeft.fontSize = 9
                aux.append(Paragraph(cell, sLeft))
            dataAux.append(aux)
        t=Table(dataAux, spaceAfter=50, spaceBefore=30)
        t.setStyle(TableStyle(style))
        elements.append(t)

        s.fontSize = 12
        elements.append(Paragraph(ugettext("18.- NIVEL DE PREFERENCIA SOCIAL NEGATIVA (IPN): PESADO"),s))
        s.fontSize = 9

        data = []
        aux = []

        aux.append(ugettext("VALOR IPN"))
        aux.append(ugettext("NIVEL IPN"))
        data.append(aux)
        aux = []
        aux.append(str(ipn[alumno]) + "%")
        aux.append(str(proposals['ipn'][alumno][list(proposals['ipn'][alumno])[0]]))
        data.append(aux)
        aux = []
        dataAux = []
        for r, row in enumerate(data):
            aux = []
            for c, cell in enumerate(row):
                if r == 0:
                    sLeft.fontName = 'Helvetica-Bold'
                    sLeft.textColor = 'black'
                else:
                    sLeft.fontName = 'Helvetica'
                    if c == 1:
                        if proposals['ipn'][alumno][list(proposals['ipn'][alumno])[0]] == gettext("Alto"):
                            sLeft.textColor = 'red'
                        else:
                            sLeft.textColor = 'black'
                    else:
                        percent = int(cell[0:-1])
                        if percent >= 75:
                            sLeft.textColor = 'red'
                        else:
                            sLeft.textColor = 'black'
                sLeft.fontSize = 9
                aux.append(Paragraph(cell, sLeft))
            dataAux.append(aux)
        t=Table(dataAux, spaceAfter=50, spaceBefore=30)
        t.setStyle(TableStyle(style))
        elements.append(t)

        elements.append(PageBreak())
        doc.pagesize = portrait(A4)


        s.fontSize = 11
        elements.append(Paragraph(ugettext("Propuesta de intervención"), s))
        s.fontSize = 10
        elements.append(Paragraph(ugettext("Áreas"), s))
        elements.append(Spacer(1, 0.1*inch))
        d = Drawing(760, 1)
        d.add(Line(0, 0, 500, 0))
        elements.append(d)
        elements.append(Spacer(1, 0.25*inch))

        listProposals = []
        for vari in proposals['recomendaciones']:
            if (not_empty(proposals['recomendaciones'][vari])):
                listProposals.append(ListItem(Paragraph(vari + ": " + return_des(proposals['recomendaciones'][vari]),sLeft), spaceAfter=10))
                firstList = []
                for varinum in proposals['recomendaciones'][vari]:
                    for ex in proposals['recomendaciones'][vari][varinum]:
                        if (not_empty_ex(proposals['recomendaciones'][vari][varinum][ex])):
                            firstList.append(ListItem(Paragraph(ex,sLeft), spaceAfter=10))
                            secondList = []
                            for num in proposals['recomendaciones'][vari][varinum][ex]:
                                for secondArea in proposals['recomendaciones'][vari][varinum][ex][num]:
                                    if len(proposals['recomendaciones'][vari][varinum][ex][num][secondArea]):
                                        secondList.append(ListItem(Paragraph(secondArea,sLeft), spaceAfter=10))
                                        for studentProp in proposals['recomendaciones'][vari][varinum][ex][num][secondArea]:
                                            reasonsList = []
                                            for i, reasons in enumerate(proposals['recomendaciones'][vari][varinum][ex][num][secondArea][studentProp]):
                                                if i != 0 and i != 1:
                                                    reasonsList.append(ListItem(Paragraph(reasons,sLeft)))
                                            secondList.append(ListItem(ListFlowable(reasonsList, bulletType='bullet', start='diamond', leftIndent=10,
                                                                                    bulletFontSize=7, bulletOffsetY=-2), bulletColor="white", spaceAfter=15))
                            firstList.append(ListItem(ListFlowable(secondList, bulletType='bullet', start='rarrowhead', leftIndent=10,
                                                                    bulletFontSize=7, bulletOffsetY=-2), bulletColor="white", spaceAfter=15))
                listProposals.append(ListItem(ListFlowable(firstList, bulletType='bullet', start='square', leftIndent=10, bulletFontSize=5,
                                                    bulletOffsetY=-3), bulletColor="white", spaceAfter=20))
        t = ListFlowable(listProposals, bulletType='bullet', bulletOffsetY=2)

        elements.append(t)

        if all == 1:
            return elements
        else:
            doc.multiBuild(elements, canvasmaker=FooterCanvas)
            pdfPrint = buffer.getvalue()
            buffer.close()
            response.write(pdfPrint)
            return response
    else:
        return render(request, 'resultados/datos_alumno.html', {'teacher':teacherProfile, 'dateAlumno': studentCurrent.idAl.fecha_nacimiento.strftime('%d/%m/%Y'),'date': test.date_created.strftime('%d/%m/%Y %H:%M'),'test': test, 'alumno': studentCurrent.idAl, 'alumnoUsername': alumno, 'respuestas': matrix, 'preguntas': preguntas, 'sp': sp[alumno], 'sn': sn[alumno],
                                                                'ep': matrix12[str(alumno)]['EP'], 'en': matrix12[str(alumno)]['EN'], 'pos': pos, 'spValue': proposals['sp'][alumno][list(proposals['sp'][alumno])[0]],
                                                                'np': np[alumno], 'snValue': proposals['sn'][alumno][list(proposals['sn'][alumno])[0]], 'nn': nn[alumno], 'rp': rp, 'rn':rn, 'os':os,
                                                                'epValue':proposals['ep'][alumno][list(proposals['ep'][alumno])[0]], 'pp': matrix34[str(alumno)]['PP'], 'pap': matrix34[str(alumno)]['PAP'], 'ppValue':proposals['pp'][alumno][list(proposals['pp'][alumno])[0]],
                                                                'papValue':proposals['pap'][alumno][list(proposals['pap'][alumno])[0]], 'enValue':proposals['en'][alumno][list(proposals['en'][alumno])[0]], 'pnValue':proposals['pn'][alumno][list(proposals['pn'][alumno])[0]],
                                                                'panValue':proposals['pan'][alumno][list(proposals['pan'][alumno])[0]], 'ippValue':proposals['ipp'][alumno][list(proposals['ipp'][alumno])[0]], 'ipnValue':proposals['ipn'][alumno][list(proposals['ipn'][alumno])[0]],
                                                                'pn': matrix34[str(alumno)]['PN'], 'pan': matrix34[str(alumno)]['PAN'], 'ipp': ipp[alumno], 'ipn': ipn[alumno], 'ip': ip[alumno], 'in': iN[alumno], 'ipValue':proposals['ip'][alumno][list(proposals['ip'][alumno])[0]],
                                                                'inValue':proposals['in'][alumno][list(proposals['in'][alumno])[0]], 'imp': imp[alumno], 'impValue':proposals['imp'][alumno][list(proposals['imp'][alumno])[0]], 'imn': imn[alumno], 'imnValue':proposals['imn'][alumno][list(proposals['imn'][alumno])[0]], 'oip': oip, 'oin': oin, 'recomendaciones': proposals['recomendaciones'],
                                                                'respuestasText2': matrixText[2][studentCurrent.username], 'respuestasText4': matrixText[4][studentCurrent.username], 'respuestasText6': matrixText[6][studentCurrent.username], 'year':year})
def show_results_all(request, test, year):
    test = Test.objects.get(id=test)
    preguntas = Preguntas_test.objects.filter(test=test)
    alumnos = AlumnoTests.objects.filter(idTest=test)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachement; filename="Informes-Individuales-Cuestionario-{0}.pdf"'.format(test.nombre)

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30,leftMargin=30, topMargin=100,bottomMargin=50)
    doc.pagesize = portrait(A4)
    elements = []
    for alumno in alumnos:
        if alumno.answer:
            elements.extend(show_results_student(request, test.id, alumno.username, year))
            elements.append(PageBreak())

    doc.multiBuild(elements, canvasmaker=FooterCanvas)
    pdfPrint = buffer.getvalue()
    buffer.close()
    response.write(pdfPrint)
    return response


def get_soc(sp, sn, ep, en, np, nn):
    if sp[list(sp)[0]] == ugettext("Alto") and sn[list(sn)[0]] == ugettext("Bajo") and np >= 50:
        pos = ugettext("Líder")
    elif sp[list(sp)[0]] == ugettext("Alto") and sn[list(sn)[0]] == ugettext("Bajo") and np < 50:
        pos = ugettext("Astro")
    elif sp[list(sp)[0]] == ugettext("Alto") and sn[list(sn)[0]] == ugettext("Medio"):
        pos = ugettext("Popular")
    elif sp[list(sp)[0]] == ugettext("Medio") and (sn[list(sn)[0]] == ugettext("Medio") or sn[list(sn)[0]] == ugettext("Bajo")) and (ep[list(ep)[0]] == ugettext("Alto") or ep[list(ep)[0]] == ugettext("Medio")):
        pos = ugettext("Integrado")
    elif sp[list(sp)[0]] == ugettext("Medio") and (sn[list(sn)[0]] == ugettext("Medio") or sn[list(sn)[0]] == ugettext("Bajo")) and ep[list(ep)[0]] == ugettext("Bajo"):
        pos = ugettext("Solitario")
    elif sp[list(sp)[0]] == ugettext("Alto") and sn[list(sn)[0]] == ugettext("Alto"):
        pos = ugettext("Polémico")
    elif sp[list(sp)[0]] == ugettext("Medio") and sn[list(sn)[0]] == ugettext("Alto"):
        pos = ugettext("Rechazo Parcial")
    elif sp[list(sp)[0]] == ugettext("Bajo") and sn[list(sn)[0]] == ugettext("Alto"):
        pos = ugettext("Rechazo Total")
    elif sp[list(sp)[0]] == ugettext("Bajo") and (sn[list(sn)[0]] == ugettext("Medio") or sn[list(sn)[0]] == ugettext("Bajo")) and ep[list(ep)[0]] == ugettext("Alto"):
        pos = ugettext("Desatendido")
    elif sp[list(sp)[0]] == ugettext("Bajo") and (sn[list(sn)[0]] == ugettext("Medio") or sn[list(sn)[0]] == ugettext("Bajo")) and ep[list(ep)[0]] == ugettext("Medio"):
        pos = ugettext("Ignorado")
    elif sp[list(sp)[0]] == ugettext("Bajo") and (sn[list(sn)[0]] == ugettext("Medio") or sn[list(sn)[0]] == ugettext("Bajo")) and ep[list(ep)[0]] == ugettext("Bajo"):
        pos = ugettext("Aislado")
    elif sp[list(sp)[0]] == ugettext("Bajo") and sn[list(sn)[0]] == ugettext("Medio"):
        pos = ugettext("Eminencia gris, elegido por el líder")
    else:
        pos = ''
    return pos

def get_proposals(sp, np, nn, sn, spval, snval, imp, ipval, imn, inval, iN, ip, ipp, ipval5, ipn, inval6, data1, data2, data3, data4, n, matrix12, matrix34, matrix, alumnoCurrent, matrixText, grupo_edad):
    spValue = {}
    snValue = {}
    npValue = {}
    nnValue = {}
    impValue = {}
    imnValue = {}
    ipValue = {}
    inValue = {}
    ipnValue = {}
    ippValue = {}

    rpValue = {}
    rnValue = {}
    epValue = {}
    ppValue = {}
    papValue = {}
    enValue = {}
    pnValue = {}
    panValue = {}


    for s in spval:
        np[s] = int((float(spval[s]) / ((n - 1) * 5)) * 100)
        nn[s] = int((float(snval[s]) / ((n - 1) * 5)) * 100)
        imp[s] = int((float(ipval[s]) / ((n - 1) * 5)) * 100)
        imn[s] = int((float(inval[s]) / ((n - 1) * 5)) * 100)
        ipp[s] = int((float(ipval5[s]) / ((n - 1) * 5)) * 100)
        ipn[s] = int((float(inval6[s]) / ((n - 1) * 5)) * 100)

        if sp[s] >= data1[7]['Xsup']:
            spValue[s] = {sp[s]: ugettext("Alto")}
        elif data1[8]['Xinf'] <= sp[s] < data1[7]['Xsup']:
            spValue[s] = {sp[s]: ugettext("Medio")}
        else:
            spValue[s] = {sp[s]: ugettext("Bajo")}

        if sn[s] >= data2[7]['Xsup']:
            snValue[s] = {sn[s]: ugettext("Alto")}
        elif data2[8]['Xinf'] <= sn[s] < data2[7]['Xsup']:
            snValue[s] = {sn[s]: ugettext("Medio")}
        else:
            snValue[s] = {sn[s]: ugettext("Bajo")}

        if ip[s] >= data3[7]['Xsup']:
            ipValue[s] = {ip[s]: ugettext("Alto")}
        elif data3[8]['Xinf'] <= ip[s] < data3[7]['Xsup']:
            ipValue[s] = {ip[s]: ugettext("Medio")}
        else:
            ipValue[s] = {ip[s]: ugettext("Bajo")}

        if iN[s] >= data4[7]['Xsup']:
            inValue[s] = {iN[s]: ugettext("Alto")}
        elif data4[8]['Xinf'] <= iN[s] < data4[7]['Xsup']:
            inValue[s] = {iN[s]: ugettext("Medio")}
        else:
            inValue[s] = {iN[s]: ugettext("Bajo")}

        if np[s] >= 75:
            npValue[s] = {np[s]: ugettext("Alto")}
        elif 26 <= np[s] <= 74:
            npValue[s] = {np[s]: ugettext("Medio")}
        else:
            npValue[s] = {np[s]: ugettext("Bajo")}

        if nn[s] >= 75:
            nnValue[s] = {nn[s]: ugettext("Alto")}
        elif 26 <= nn[s] <= 74:
            nnValue[s] = {nn[s]: ugettext("Medio")}
        else:
            nnValue[s] = {nn[s]: ugettext("Bajo")}

        if imp[s] >= 75:
            impValue[s] = {imp[s]: ugettext("Alto")}
        elif 26 <= imp[s] <= 74:
            impValue[s] = {imp[s]: ugettext("Medio")}
        else:
            impValue[s] = {imp[s]: ugettext("Bajo")}

        if imn[s] >= 75:
            imnValue[s] = {imn[s]: ugettext("Alto")}
        elif 26 <= imn[s] <= 74:
            imnValue[s] = {imn[s]: ugettext("Medio")}
        else:
            imnValue[s] = {imn[s]: ugettext("Bajo")}

        if ipp[s] >= 75:
            ippValue[s] = {ipp[s]: ugettext("Alto")}
        elif 26 <= ipp[s] <= 74:
            ippValue[s] = {ipp[s]: ugettext("Medio")}
        else:
            ippValue[s] = {ipp[s]: ugettext("Bajo")}

        if ipn[s] >= 75:
            ipnValue[s] = {ipn[s]: ugettext("Alto")}
        elif 26 <= ipn[s] <= 74:
            ipnValue[s] = {ipn[s]: ugettext("Medio")}
        else:
            ipnValue[s] = {ipn[s]: ugettext("Bajo")}


    ic, id, iap, ian = 0, 0, 0, 0
    for m in matrix12:
        for e in matrix12[m]:
            if e == "EP" or e == "EN":
                matrix12[m][e] = int((float(matrix12[m][e]) / MAX_POINTS) * 100)
                if e == "EP":
                    if matrix12[m][e] >= 75:
                        epValue[m] = {matrix12[m][e]: ugettext("Alto")}
                    elif 26 <= matrix12[m][e] <= 74:
                        epValue[m] = {matrix12[m][e]: ugettext("Medio")}
                    else:
                        epValue[m] = {matrix12[m][e]: ugettext("Bajo")}
                else:
                    if matrix12[m][e] >= 75:
                        enValue[m] = {matrix12[m][e]: ugettext("Alto")}
                    elif 26 <= matrix12[m][e] <= 74:
                        enValue[m] = {matrix12[m][e]: ugettext("Medio")}
                    else:
                        enValue[m] = {matrix12[m][e]: ugettext("Bajo")}
            elif e == "RP":
                ic += matrix12[m][e]
                if matrix12[m][e] > 0:
                    rpValue[m] = {matrix12[m][e]: "Mayor"}
                else:
                    rpValue[m] = {matrix12[m][e]: "Cero"}
            elif e == "RN":
                id += matrix12[m][e]
                if matrix12[m][e] > 0:
                    rnValue[m] = {matrix12[m][e]: "Mayor"}
                else:
                    rnValue[m] = {matrix12[m][e]: "Cero"}

    for m in matrix34:
        for e in matrix34[m]:
            if e == "PAP":
                if matrix34[m]['PP'] != 0:
                    matrix34[m][e] = int((float(matrix34[m][e]) / matrix34[m]['PP']) * 100)
                else:
                    matrix34[m][e] = 0
                if matrix34[m][e] >= 75:
                    papValue[m] = {matrix34[m][e]: ugettext("Alto")}
                elif 26 <= matrix34[m][e] <= 74:
                    papValue[m] = {matrix34[m][e]: ugettext("Medio")}
                else:
                    papValue[m] = {matrix34[m][e]: ugettext("Bajo")}
            elif e == "PAN":
                if matrix34[m]['PN'] != 0:
                    matrix34[m][e] = int((float(matrix34[m][e]) / matrix34[m]['PN']) * 100)
                else:
                    matrix34[m][e] = 0
                if matrix34[m][e] >= 75:
                    panValue[m] = {matrix34[m][e]: ugettext("Alto")}
                elif 26 <= matrix34[m][e] <= 74:
                    panValue[m] = {matrix34[m][e]: ugettext("Medio")}
                else:
                    panValue[m] = {matrix34[m][e]: ugettext("Bajo")}
    for m in matrix34:
        for e in matrix34[m]:
            if e == "PP" or e == "PN":
                matrix34[m][e] = int((float(matrix34[m][e]) / MAX_POINTS) * 100)
                if e == "PP":
                    if matrix34[m][e] >= 75:
                        ppValue[m] = {matrix34[m][e]: ugettext("Alto")}
                    elif 26 <= matrix34[m][e] <= 74:
                        ppValue[m] = {matrix34[m][e]: ugettext("Medio")}
                    else:
                        ppValue[m] = {matrix34[m][e]: ugettext("Bajo")}
                else:
                    if matrix34[m][e] >= 75:
                        pnValue[m] = {matrix34[m][e]: ugettext("Alto")}
                    elif 26 <= matrix34[m][e] <= 74:
                        pnValue[m] = {matrix34[m][e]: ugettext("Medio")}
                    else:
                        pnValue[m] = {matrix34[m][e]: ugettext("Bajo")}

    ic = int((float(ic) / ((n -1)*MAX_POINTS)) *100)
    id = int((float(id) / ((n -1)*MAX_POINTS)) *100)
    iap = int((float(sum(sp.values())) / (MAX_POINTS * n)) * 100)
    ian = int((float(sum(sn.values())) / (MAX_POINTS * n)) * 100)
    if ic >= 75:
        icValue = {ic: ugettext("Alto")}
    elif 45 <= ic <= 74:
        icValue = {ic: ugettext("Medio")}
    elif 25 <= ic <= 44:
        icValue = {ic: ugettext("Bajo")}
    else:
        icValue = {ic: ugettext("Muy bajo")}

    if id >= 75:
        idValue = {id: ugettext("Muy alto")}
    elif 45 <= id <= 74:
        idValue = {id: ugettext("Alto")}
    elif 25 <= id <= 44:
        idValue = {id: ugettext("Medio")}
    else:
        idValue = {id: ugettext("Bajo")}

    if iap >= 75:
        iapValue = {iap: ugettext("Alto")}
    elif 45 <= iap <= 74:
        iapValue = {iap: ugettext("Medio")}
    elif 25 <= iap <= 44:
        iapValue = {iap: ugettext("Bajo")}
    else:
        iapValue = {iap: ugettext("Muy bajo")}

    if ian >= 75:
        ianValue = {ian: ugettext("Muy alto")}
    elif 45 <= ian <= 74:
        ianValue = {ian: ugettext("Alto")}
    elif 25 <= ian <= 44:
        ianValue = {ian: ugettext("Medio")}
    else:
        ianValue = {ian: ugettext("Bajo")}


    oipValue = {}
    oinValue = {}
    osValue = {}


    for al in matrix[3]:
        aux = []
        for al2 in matrix[3][al]:
            if "#ed3e46" in matrix[3][al][al2]:
                aux.append(al2)
        oipValue[al] = aux

    for al in matrix[4]:
        aux = []
        for al2 in matrix[4][al]:
            if "#9646e0" in matrix[4][al][al2]:
                aux.append(al2)
        oinValue[al] = aux

    for al in matrix[1]:
        aux = {}
        for al2 in matrix[1][al]:
            reasonsOs = ' '
            if "#e05ab8" in matrix[1][al][al2]:
                if alumnoCurrent != '':
                    o = AlumnoTests.objects.get(username=al2)
                    if matrixText[2][al2][al] != '':
                        reasonsOs = ugettext('Elige a ') + o.get_nombre() + " " + o.get_apellidos() + ugettext(' pero ') + o.get_nombre() + " " + o.get_apellidos() + ugettext(' lo/la rechaza por el motivo "') + matrixText[2][al2][al] + '".'
                    else:
                        reasonsOs = ugettext('Elige a ') + o.get_nombre() + " " + o.get_apellidos() + ugettext(' pero ') + o.get_nombre() + " " + o.get_apellidos() + ugettext(' lo/la rechaza') + '.'

                aux[al2] = reasonsOs
        if alumnoCurrent != '':
            for al3 in matrix[2][al]:
                reasonsOs = ' '
                if "#e05ab8" in matrix[2][al][al3]:
                    o = AlumnoTests.objects.get(username=al3)
                    if matrixText[2][al][al3] != '':
                        reasonsOs = ugettext('Rechaza a ') + o.get_nombre() + " " + o.get_apellidos() + ugettext(' por el motivo "') + matrixText[2][al][al3] + ugettext('" y ') + o.get_nombre() + " " + o.get_apellidos() + ugettext(' lo elige') + '.'
                    else:
                        reasonsOs = ugettext('Rechaza a ') + o.get_nombre() + " " + o.get_apellidos() + ugettext(' y ') + o.get_nombre() + " " + o.get_apellidos() + ugettext(' lo elige') + '.'

                    aux[al3] = reasonsOs
        osValue[al] = aux

    grupo_edad_name = Grupo_edad.objects.get(id=grupo_edad).grupoedad
    etapa = Link.objects.get(name=grupo_edad_name).url
    URL = "https://www.atopa.es/"
    recommendations = {}
    recommendations['IC'] = {1: {ugettext('Educación en valores'): {1: {ugettext('Interculturalidad'): {}}, 2: {ugettext('Respeto y tolerancia'): {}}, 3: {ugettext('Solidaridad'): {}}, 4: {ugettext('Responsabilidad'): {}}}}, 2: {ugettext('Grupo y aula'): {1: {ugettext('Cohesión de grupo'): {}}, 2: {ugettext('Gestión de aula'): {}}, 3: {ugettext('Trabajo colaborativo y cooperativo'): {}}}}}
    recommendations['ID'] = {1: {ugettext('Educación emocional'): {1: {ugettext('Autoconcepto y autoestima'): {}}, 2: {ugettext('Autoregulación'): {}}, 3: {ugettext('Habilidades sociales'): {}}, 4: {ugettext('Empatía'): {}}, 5: {ugettext('Resolución de conflictos'): {}}}}, 2: {ugettext('Educación en valores'): {1: {ugettext('Interculturalidad'): {}}, 2: {ugettext('Solidaridad'): {}}}}, 3: {ugettext('Grupo y aula'): {1: {ugettext('Cohesión de grupo'): {}}, 2: {ugettext('Gestión de aula'): {}}, 3: {ugettext('Trabajo colaborativo y cooperativo'): {}}}}}
    recommendations['SP'] = {1: {ugettext('Educación en valores'): {1: {ugettext('Interculturalidad'): {}}, 2: {ugettext('Respeto y tolerancia'): {}}, 3: {ugettext('Solidaridad'): {}}, 4: {ugettext('Responsabilidad'): {}}}}, 2: {ugettext('Grupo y aula'): {1: {ugettext('Cohesión de grupo'): {}}, 2: {ugettext('Gestión de aula'): {}}, 3: {ugettext('Trabajo colaborativo y cooperativo'): {}}}}}
    recommendations['SN'] = {1: {ugettext('Educación emocional'): {1: {ugettext('Autoconcepto y autoestima'): {}}, 2: {ugettext('Autoregulación'): {}}, 3: {ugettext('Habilidades sociales'): {}}, 4: {ugettext('Empatía'): {}}, 5: {ugettext('Resolución de conflictos'): {}}}}, 2: {ugettext('Educación en valores'): {1: {ugettext('Interculturalidad'): {}}, 2: {ugettext('Respeto y tolerancia'): {}}, 3: {ugettext('Solidaridad'): {}}, 4: {ugettext('Responsabilidad'): {}}}}}
    recommendations['RP'] = {1: {ugettext('Educación emocional'): {1: {ugettext('Autoconcepto y autoestima'): {}}, 2: {ugettext('Autoregulación'): {}}, 3: {ugettext('Habilidades sociales'): {}}, 4: {ugettext('Empatía'): {}}, 5: {ugettext('Resolución de conflictos'): {}}}}, 2: {ugettext('Grupo y aula'): {1: {ugettext('Cohesión de grupo'): {}}, 2: {ugettext('Gestión de aula'): {}}, 3: {ugettext('Trabajo colaborativo y cooperativo'): {}}}}}
    recommendations['RN'] = {1: {ugettext('Educación emocional'): {1: {ugettext('Autoconcepto y autoestima'): {}}, 2: {ugettext('Autoregulación'): {}}, 3: {ugettext('Habilidades sociales'): {}}, 4: {ugettext('Empatía'): {}}, 5: {ugettext('Resolución de conflictos'): {}}}}, 2: {ugettext('Educación en valores'): {1: {ugettext('Interculturalidad'): {}}, 2: {ugettext('Respeto y tolerancia'): {}}, 3: {ugettext('Solidaridad'): {}}, 4: {ugettext('Responsabilidad'): {}}}}}
    recommendations['OS'] = {1: {ugettext('Educación emocional'): {1: {ugettext('Autoconcepto y autoestima'): {}}, 2: {ugettext('Autoregulación'): {}}, 3: {ugettext('Habilidades sociales'): {}}, 4: {ugettext('Empatía'): {}}, 5: {ugettext('Resolución de conflictos'): {}}}}}
    recommendations['EP'] = {1: {ugettext('Educación emocional'): {1: {ugettext('Autoconcepto y autoestima'): {}}, 2: {ugettext('Autoregulación'): {}}, 3: {ugettext('Habilidades sociales'): {}}, 4: {ugettext('Empatía'): {}}, 5: {ugettext('Resolución de conflictos'): {}}}}, 2: {ugettext('Educación en valores'): {1: {ugettext('Interculturalidad'): {}}, 2: {ugettext('Respeto y tolerancia'): {}}, 3: {ugettext('Solidaridad'): {}}, 4: {ugettext('Responsabilidad'): {}}}}, 3: {ugettext('Grupo y aula'): {1: {ugettext('Cohesión de grupo'): {}}, 2: {ugettext('Gestión de aula'): {}}, 3: {ugettext('Trabajo colaborativo y cooperativo'): {}}}}}
    recommendations['PP'] = {1: {ugettext('Educación emocional'): {1: {ugettext('Autoconcepto y autoestima'): {}}, 2: {ugettext('Autoregulación'): {}}, 3: {ugettext('Habilidades sociales'): {}}, 4: {ugettext('Empatía'): {}}, 5: {ugettext('Resolución de conflictos'): {}}}}, 2: {ugettext('Educación en valores'): {1: {ugettext('Interculturalidad'): {}}, 2: {ugettext('Respeto y tolerancia'): {}}, 3: {ugettext('Solidaridad'): {}}, 4: {ugettext('Responsabilidad'): {}}}}, 3: {ugettext('Grupo y aula'): {1: {ugettext('Cohesión de grupo'): {}}, 2: {ugettext('Gestión de aula'): {}}, 3: {ugettext('Trabajo colaborativo y cooperativo'): {}}}}}
    recommendations['EN'] = {1: {ugettext('Educación emocional'): {1: {ugettext('Autoconcepto y autoestima'): {}}, 2: {ugettext('Autoregulación'): {}}, 3: {ugettext('Habilidades sociales'): {}}, 4: {ugettext('Empatía'): {}}, 5: {ugettext('Resolución de conflictos'): {}}}}, 2: {ugettext('Educación en valores'): {1: {ugettext('Interculturalidad'): {}}, 2: {ugettext('Respeto y tolerancia'): {}}, 3: {ugettext('Solidaridad'): {}}, 4: {ugettext('Responsabilidad'): {}}}}}
    recommendations['PN'] = {1: {ugettext('Educación emocional'): {1: {ugettext('Autoconcepto y autoestima'): {}}, 2: {ugettext('Autoregulación'): {}}, 3: {ugettext('Habilidades sociales'): {}}, 4: {ugettext('Empatía'): {}}, 5: {ugettext('Resolución de conflictos'): {}}}}, 2: {ugettext('Educación en valores'): {1: {ugettext('Interculturalidad'): {}}, 2: {ugettext('Respeto y tolerancia'): {}}, 3: {ugettext('Solidaridad'): {}}, 4: {ugettext('Responsabilidad'): {}}}}}
    
    recommendations['OIP'] = {1:{ugettext('Educación emocional'): {1: {ugettext('Autoconcepto y autoestima'): {}}, 2: {ugettext('Autoregulación'): {}}, 3: {ugettext('Habilidades sociales'): {}}, 4: {ugettext('Empatía'): {}}, 5: {ugettext('Resolución de conflictos'): {}}}}}
    recommendations['OIN'] = {1: {ugettext('Educación emocional'): {1: {ugettext('Autoconcepto y autoestima'): {}}, 2: {ugettext('Autoregulación'): {}}, 3: {ugettext('Habilidades sociales'): {}}, 4: {ugettext('Empatía'): {}}, 5: {ugettext('Resolución de conflictos'): {}}}}}
    recommendations['IP'] = {1: {ugettext('Educación emocional'): {1: {ugettext('Autoconcepto y autoestima'): {}}, 2: {ugettext('Autoregulación'): {}}, 3: {ugettext('Habilidades sociales'): {}}, 4: {ugettext('Empatía'): {}}, 5: {ugettext('Resolución de conflictos'): {}}}}}
    recommendations['IN'] = {1: {ugettext('Educación emocional'): {1: {ugettext('Autoconcepto y autoestima'): {}}, 2: {ugettext('Autoregulación'): {}}, 3: {ugettext('Habilidades sociales'): {}}, 4: {ugettext('Empatía'): {}}, 5: {ugettext('Resolución de conflictos'): {}}}}}
    recommendations['IPN'] = {1: {ugettext('Educación emocional'): {1: {ugettext('Autoconcepto y autoestima'): {}}, 2: {ugettext('Autoregulación'): {}}, 3: {ugettext('Habilidades sociales'): {}}, 4: {ugettext('Empatía'): {}}, 5: {ugettext('Resolución de conflictos'): {}}}}, 2: {ugettext('Educación en valores'): {1: {ugettext('Interculturalidad'): {}}, 2: {ugettext('Respeto y tolerancia'): {}}, 3: {ugettext('Solidaridad'): {}}, 4: {ugettext('Responsabilidad'): {}}}}}


    if alumnoCurrent == '':

        if icValue[list(icValue)[0]] == ugettext("Bajo"):

            if ugettext('Grupo') not in recommendations['IC'][2][ugettext('Grupo y aula')][1][ugettext('Cohesión de grupo')]:
                recommendations['IC'][2][ugettext('Grupo y aula')][1][ugettext('Cohesión de grupo')][ugettext('Grupo')] = []
                recommendations['IC'][2][ugettext('Grupo y aula')][1][ugettext('Cohesión de grupo')][ugettext('Grupo')].append(URL + etapa +"/" + Link.objects.get(name="Grupo y aula").url + "/" + etapa.split('_')[1] + "_" + Link.objects.get(name="Cohesión de grupo").url + '.php')
            recommendations['IC'][2][ugettext('Grupo y aula')][1][ugettext('Cohesión de grupo')][ugettext('Grupo')].append(ugettext('El índice de cohesión (IC) del grupo es bajo.'))
            recommendations['IC'][2][ugettext('Grupo y aula')][1][ugettext('Cohesión de grupo')][ugettext('Grupo')].append(ugettext('Se recomienda trabajar esta categoría en grupos de nueva creación donde los integrantes no se conozcan.'))

            if ugettext('Grupo') not in recommendations['IC'][2][ugettext('Grupo y aula')][3][ugettext('Trabajo colaborativo y cooperativo')]:
                recommendations['IC'][2][ugettext('Grupo y aula')][3][ugettext('Trabajo colaborativo y cooperativo')][ugettext('Grupo')] = []
                recommendations['IC'][2][ugettext('Grupo y aula')][3][ugettext('Trabajo colaborativo y cooperativo')][ugettext('Grupo')].append(URL + etapa +"/" + Link.objects.get(name="Grupo y aula").url + "/" + etapa.split('_')[1] + "_" + Link.objects.get(name="Trabajo colaborativo y cooperativo").url + '.php')
            recommendations['IC'][2][ugettext('Grupo y aula')][3][ugettext('Trabajo colaborativo y cooperativo')][ugettext('Grupo')].append(ugettext('El índice de cohesión (IC) del grupo es bajo.'))
            recommendations['IC'][2][ugettext('Grupo y aula')][3][ugettext('Trabajo colaborativo y cooperativo')][ugettext('Grupo')].append(ugettext('Se recomienda trabajar esta categoría en grupos donde se observen configuraciones sociométricas de grupos aislados (islas, parejas, triángulos en clique) o cadenas.'))

            if ugettext('Grupo') not in recommendations["IC"][1][ugettext('Educación en valores')][1][ugettext('Interculturalidad')]:
                recommendations["IC"][1][ugettext('Educación en valores')][1][ugettext('Interculturalidad')][ugettext('Grupo')] = []
                recommendations["IC"][1][ugettext('Educación en valores')][1][ugettext('Interculturalidad')][ugettext('Grupo')].append(URL + etapa +"/" + Link.objects.get(name="Educación en valores").url + "/" + etapa.split('_')[1] + "_" + Link.objects.get(name="Interculturalidad").url + '.php')
            recommendations["IC"][1][ugettext('Educación en valores')][1][ugettext('Interculturalidad')][ugettext('Grupo')].append(ugettext('El índice de cohesión (IC) del grupo es bajo.'))
            recommendations["IC"][1][ugettext('Educación en valores')][1][ugettext('Interculturalidad')][ugettext('Grupo')].append(ugettext('Se recomienda trabajar esta categoría en grupos en los que se dé la circunstancia de la multiculturalidad (raza, etnia, religión, etc.).'))

            if ugettext('Grupo') not in recommendations['IC'][1][ugettext('Educación en valores')][3][ugettext('Solidaridad')]:
                recommendations['IC'][1][ugettext('Educación en valores')][3][ugettext('Solidaridad')][ugettext('Grupo')] = []
                recommendations['IC'][1][ugettext('Educación en valores')][3][ugettext('Solidaridad')][ugettext('Grupo')].append(URL + etapa +"/" + Link.objects.get(name="Educación en valores").url + "/" + etapa.split('_')[1] + "_" + Link.objects.get(name="Solidaridad").url + '.php')
            recommendations['IC'][1][ugettext('Educación en valores')][3][ugettext('Solidaridad')][ugettext('Grupo')].append(ugettext('El índice de cohesión (IC) del grupo es bajo.'))
            recommendations['IC'][1][ugettext('Educación en valores')][3][ugettext('Solidaridad')][ugettext('Grupo')].append(ugettext('Se recomienda trabajar esta categoría en grupos en los que puedan existir desequilibrios socioeconómicos.'))



        if icValue[list(icValue)[0]] == ugettext("Muy bajo") and iapValue[list(iapValue)[0]] == ugettext("Muy bajo"):

            if ugettext('Grupo') not in recommendations['IC'][2][ugettext('Grupo y aula')][1][ugettext('Cohesión de grupo')]:
                recommendations['IC'][2][ugettext('Grupo y aula')][1][ugettext('Cohesión de grupo')][ugettext('Grupo')] = []
                recommendations['IC'][2][ugettext('Grupo y aula')][1][ugettext('Cohesión de grupo')][ugettext('Grupo')].append(URL + etapa +"/" + Link.objects.get(name="Grupo y aula").url + "/" + etapa.split('_')[1] + "_" + Link.objects.get(name="Cohesión de grupo").url + '.php')
            recommendations['IC'][2][ugettext('Grupo y aula')][1][ugettext('Cohesión de grupo')][ugettext('Grupo')].append(ugettext('El índice de cohesión (IC) y el de actividad positiva (IAP) del grupo son muy bajos.'))
            recommendations['IC'][2][ugettext('Grupo y aula')][1][ugettext('Cohesión de grupo')][ugettext('Grupo')].append(ugettext('Se recomienda trabajar esta categoría en grupos de nueva creación donde los integrantes no se conozcan.'))

            if ugettext('Grupo') not in recommendations['IC'][2][ugettext('Grupo y aula')][3][ugettext('Trabajo colaborativo y cooperativo')]:
                recommendations['IC'][2][ugettext('Grupo y aula')][3][ugettext('Trabajo colaborativo y cooperativo')][ugettext('Grupo')] = []
                recommendations['IC'][2][ugettext('Grupo y aula')][3][ugettext('Trabajo colaborativo y cooperativo')][ugettext('Grupo')].append(URL + etapa +"/" + Link.objects.get(name="Grupo y aula").url + "/" + etapa.split('_')[1] + "_" + Link.objects.get(name="Trabajo colaborativo y cooperativo").url + '.php')
            recommendations['IC'][2][ugettext('Grupo y aula')][3][ugettext('Trabajo colaborativo y cooperativo')][ugettext('Grupo')].append(ugettext('El índice de cohesión (IC) y el de actividad positiva (IAP) del grupo son muy bajos.'))
            recommendations['IC'][2][ugettext('Grupo y aula')][3][ugettext('Trabajo colaborativo y cooperativo')][ugettext('Grupo')].append(ugettext('Se recomienda trabajar esta categoría en grupos donde se observen configuraciones sociométricas de grupos aislados (islas, parejas, triángulos en clique) o cadenas.'))

            if ugettext('Grupo') not in recommendations['IC'][1][ugettext('Educación en valores')][3][ugettext('Solidaridad')]:
                recommendations['IC'][1][ugettext('Educación en valores')][3][ugettext('Solidaridad')][ugettext('Grupo')] = []
                recommendations['IC'][1][ugettext('Educación en valores')][3][ugettext('Solidaridad')][ugettext('Grupo')].append(URL + etapa +"/" + Link.objects.get(name="Educación en valores").url + "/" + etapa.split('_')[1] + "_" + Link.objects.get(name="Solidaridad").url + '.php')
            recommendations['IC'][1][ugettext('Educación en valores')][3][ugettext('Solidaridad')][ugettext('Grupo')].append(ugettext('El índice de cohesión (IC) y el de actividad positiva (IAP) del grupo son muy bajos.'))
            recommendations['IC'][1][ugettext('Educación en valores')][3][ugettext('Solidaridad')][ugettext('Grupo')].append(ugettext('Se recomienda trabajar esta categoría en grupos en los que puedan existir desequilibrios socioeconómicos.'))

            if ugettext('Grupo') not in recommendations["IC"][1][ugettext('Educación en valores')][1][ugettext('Interculturalidad')]:
                recommendations["IC"][1][ugettext('Educación en valores')][1][ugettext('Interculturalidad')][ugettext('Grupo')] = []
                recommendations["IC"][1][ugettext('Educación en valores')][1][ugettext('Interculturalidad')][ugettext('Grupo')].append(URL + etapa +"/" + Link.objects.get(name="Educación en valores").url + "/" + etapa.split('_')[1] + "_" + Link.objects.get(name="Interculturalidad").url + '.php')
            recommendations["IC"][1][ugettext('Educación en valores')][1][ugettext('Interculturalidad')][ugettext('Grupo')].append(ugettext('El índice de cohesión (IC) y el de actividad positiva (IAP) del grupo son muy bajos.'))
            recommendations["IC"][1][ugettext('Educación en valores')][1][ugettext('Interculturalidad')][ugettext('Grupo')].append(ugettext('Se recomienda trabajar esta categoría en grupos en los que se dé la circunstancia de la multiculturalidad (raza, etnia, religión, etc.).'))



        if idValue[list(idValue)[0]]== ugettext("Muy alto") and ianValue[list(ianValue)[0]] == ugettext("Muy alto"):

            if ugettext('Grupo') not in recommendations['ID'][3][ugettext('Grupo y aula')][2][ugettext('Gestión de aula')]:
                recommendations['ID'][3][ugettext('Grupo y aula')][2][ugettext('Gestión de aula')][ugettext('Grupo')] = []
                recommendations['ID'][3][ugettext('Grupo y aula')][2][ugettext('Gestión de aula')][ugettext('Grupo')].append(URL + etapa +"/" + Link.objects.get(name="Grupo y aula").url + "/" + etapa.split('_')[1] + "_" + Link.objects.get(name="Gestión de aula").url + '.php')
            recommendations['ID'][3][ugettext('Grupo y aula')][2][ugettext('Gestión de aula')][ugettext('Grupo')].append(ugettext('El índice de disociación (ID) y el de actividad negativa (IAN) son muy altos.'))
            recommendations['ID'][3][ugettext('Grupo y aula')][2][ugettext('Gestión de aula')][ugettext('Grupo')].append(ugettext('Se recomienda trabajar esta categoría en grupos en los que frecuentemente se justifiquen los rechazos en conductas molestas por parte de los compañeros o compañeras, falta de respeto a las normas, turnos de palabra, etc.'))

            if ugettext('Grupo') not in recommendations['ID'][1][ugettext('Educación emocional')][5][ugettext('Resolución de conflictos')]:
                recommendations['ID'][1][ugettext('Educación emocional')][5][ugettext('Resolución de conflictos')][ugettext('Grupo')] = []
                recommendations['ID'][1][ugettext('Educación emocional')][5][ugettext('Resolución de conflictos')][ugettext('Grupo')].append(URL + etapa +"/" + Link.objects.get(name="Educación emocional").url + "/" + etapa.split('_')[1] + "_" + Link.objects.get(name="Resolución de conflictos").url + '.php')
            recommendations['ID'][1][ugettext('Educación emocional')][5][ugettext('Resolución de conflictos')][ugettext('Grupo')].append(ugettext('El índice de disociación (ID) y el de actividad negativa (IAN) son muy altos.'))
            recommendations['ID'][1][ugettext('Educación emocional')][5][ugettext('Resolución de conflictos')][ugettext('Grupo')].append(ugettext('Se recomienda trabajar esta categoría en grupos donde se observen configuraciones sociométricas de grupos o islas enfrentadas.'))

            if ugettext('Grupo') not in recommendations['ID'][1][ugettext('Educación emocional')][3][ugettext('Habilidades sociales')]:
                recommendations['ID'][1][ugettext('Educación emocional')][3][ugettext('Habilidades sociales')][ugettext('Grupo')] = []
                recommendations['ID'][1][ugettext('Educación emocional')][3][ugettext('Habilidades sociales')][ugettext('Grupo')].append(URL + etapa +"/" + Link.objects.get(name="Educación emocional").url + "/" + etapa.split('_')[1] + "_" + Link.objects.get(name="Habilidades sociales").url + '.php')
            recommendations['ID'][1][ugettext('Educación emocional')][3][ugettext('Habilidades sociales')][ugettext('Grupo')].append(ugettext('El índice de disociación (ID) y el de actividad negativa (IAN) son muy altos.'))
            recommendations['ID'][1][ugettext('Educación emocional')][3][ugettext('Habilidades sociales')][ugettext('Grupo')].append(ugettext('Se recomienda trabajar esta categoría en grupos donde las respuestas a los rechazos se motiven en actitudes de “falta de educación” “falta de agradecimiento o ayuda” expresado con respuestas tipo “me contesta mal”, “me chincha”, etc.'))

            if ugettext('Grupo') not in recommendations['ID'][3][ugettext('Grupo y aula')][1][ugettext('Cohesión de grupo')]:
                recommendations['ID'][3][ugettext('Grupo y aula')][1][ugettext('Cohesión de grupo')][ugettext('Grupo')] = []
                recommendations['ID'][3][ugettext('Grupo y aula')][1][ugettext('Cohesión de grupo')][ugettext('Grupo')].append(URL + etapa +"/" + Link.objects.get(name="Grupo y aula").url + "/" + etapa.split('_')[1] + "_" + Link.objects.get(name="Cohesión de grupo").url + '.php')
            recommendations['ID'][3][ugettext('Grupo y aula')][1][ugettext('Cohesión de grupo')][ugettext('Grupo')].append(ugettext('El índice de disociación (ID) y el de actividad negativa (IAN) son muy altos.'))
            recommendations['ID'][3][ugettext('Grupo y aula')][1][ugettext('Cohesión de grupo')][ugettext('Grupo')].append(ugettext('Se recomienda trabajar esta categoría en grupos donde los rechazos puedan estar motivados por falta de confianza.'))

            if ugettext('Grupo') not in recommendations['ID'][3][ugettext('Grupo y aula')][3][ugettext('Trabajo colaborativo y cooperativo')]:
                recommendations['ID'][3][ugettext('Grupo y aula')][3][ugettext('Trabajo colaborativo y cooperativo')][ugettext('Grupo')] = []
                recommendations['ID'][3][ugettext('Grupo y aula')][3][ugettext('Trabajo colaborativo y cooperativo')][ugettext('Grupo')].append(URL + etapa +"/" + Link.objects.get(name="Grupo y aula").url + "/" + etapa.split('_')[1] + "_" + Link.objects.get(name="Trabajo colaborativo y cooperativo").url + '.php')
            recommendations['ID'][3][ugettext('Grupo y aula')][3][ugettext('Trabajo colaborativo y cooperativo')][ugettext('Grupo')].append(ugettext('El índice de disociación (ID) y el de actividad negativa (IAN) son muy altos.'))
            recommendations['ID'][3][ugettext('Grupo y aula')][3][ugettext('Trabajo colaborativo y cooperativo')][ugettext('Grupo')].append(ugettext('Se recomienda trabajar esta categoría en grupos donde se observen configuraciones sociométricas de grupos enfrentados.'))

            if ugettext('Grupo') not in recommendations['ID'][2][ugettext('Educación en valores')][3][ugettext('Solidaridad')]:
                recommendations['ID'][2][ugettext('Educación en valores')][3][ugettext('Solidaridad')][ugettext('Grupo')] = []
                recommendations['ID'][2][ugettext('Educación en valores')][3][ugettext('Solidaridad')][ugettext('Grupo')].append(URL + etapa +"/" + Link.objects.get(name="Educación en valores").url + "/" + etapa.split('_')[1] + "_" + Link.objects.get(name="Solidaridad").url + '.php')
            recommendations['ID'][2][ugettext('Educación en valores')][3][ugettext('Solidaridad')][ugettext('Grupo')].append(ugettext('El índice de disociación (ID) y el de actividad negativa (IAN) son muy altos.'))
            recommendations['ID'][2][ugettext('Educación en valores')][3][ugettext('Solidaridad')][ugettext('Grupo')].append(ugettext('Se recomienda trabajar esta categoría en grupos en los que puedan existir desequilibrios socioeconómicos.'))

            if ugettext('Grupo') not in recommendations["ID"][1][ugettext('Educación en valores')][1][ugettext('Interculturalidad')]:
                recommendations["ID"][1][ugettext('Educación en valores')][1][ugettext('Interculturalidad')][ugettext('Grupo')] = []
                recommendations["ID"][1][ugettext('Educación en valores')][1][ugettext('Interculturalidad')][ugettext('Grupo')].append(URL + etapa +"/" + Link.objects.get(name="Educación en valores").url + "/" + etapa.split('_')[1] + "_" + Link.objects.get(name="Interculturalidad").url + '.php')
            recommendations["ID"][1][ugettext('Educación en valores')][1][ugettext('Interculturalidad')][ugettext('Grupo')].append(ugettext('El índice de disociación (ID) y el de actividad negativa (IAN) son muy altos.'))
            recommendations["ID"][1][ugettext('Educación en valores')][1][ugettext('Interculturalidad')][ugettext('Grupo')].append(ugettext('Se recomienda trabajar esta categoría en grupos en los que se dé la circunstancia de la multiculturalidad (raza, etnia, religión, etc.).'))


        if idValue[list(idValue)[0]]== ugettext("Alto"):

            if ugettext('Grupo') not in recommendations['ID'][3][ugettext('Grupo y aula')][2][ugettext('Gestión de aula')]:
                recommendations['ID'][3][ugettext('Grupo y aula')][2][ugettext('Gestión de aula')][ugettext('Grupo')] = []
                recommendations['ID'][3][ugettext('Grupo y aula')][2][ugettext('Gestión de aula')][ugettext('Grupo')].append(URL + etapa +"/" + Link.objects.get(name="Grupo y aula").url + "/" + etapa.split('_')[1] + "_" + Link.objects.get(name="Gestión de aula").url + '.php')
            recommendations['ID'][3][ugettext('Grupo y aula')][2][ugettext('Gestión de aula')][ugettext('Grupo')].append(ugettext('El índice de disociación (ID) es alto.'))
            recommendations['ID'][3][ugettext('Grupo y aula')][2][ugettext('Gestión de aula')][ugettext('Grupo')].append(ugettext('Se recomienda trabajar esta categoría en grupos donde frecuentemente se justifiquen los rechazos en conductas molestas por parte de los compañeros o compañeras, falta de respeto a las normas, turnos de palabra, etc.'))


            if ugettext('Grupo') not in recommendations['ID'][1][ugettext('Educación emocional')][3][ugettext('Habilidades sociales')]:
                recommendations['ID'][1][ugettext('Educación emocional')][3][ugettext('Habilidades sociales')][ugettext('Grupo')] = []
                recommendations['ID'][1][ugettext('Educación emocional')][3][ugettext('Habilidades sociales')][ugettext('Grupo')].append(URL + etapa +"/" + Link.objects.get(name="Educación emocional").url + "/" + etapa.split('_')[1] + "_" + Link.objects.get(name="Habilidades sociales").url + '.php')
            recommendations['ID'][1][ugettext('Educación emocional')][3][ugettext('Habilidades sociales')][ugettext('Grupo')].append(ugettext('El índice de disociación (ID) es alto.'))
            recommendations['ID'][1][ugettext('Educación emocional')][3][ugettext('Habilidades sociales')][ugettext('Grupo')].append(ugettext('Se recomienda trabajar esta categoría en grupos donde las respuestas a los rechazos se motiven en actitudes de “falta de educación” “falta de agradecimiento o ayuda” expresado con respuestas tipo “me contesta mal”, “me chincha”, etc.'))

            if ugettext('Grupo') not in recommendations['ID'][1][ugettext('Educación emocional')][5][ugettext('Resolución de conflictos')]:
                recommendations['ID'][1][ugettext('Educación emocional')][5][ugettext('Resolución de conflictos')][ugettext('Grupo')] = []
                recommendations['ID'][1][ugettext('Educación emocional')][5][ugettext('Resolución de conflictos')][ugettext('Grupo')].append(URL + etapa +"/" + Link.objects.get(name="Educación emocional").url + "/" + etapa.split('_')[1] + "_" + Link.objects.get(name="Resolución de conflictos").url + '.php')
            recommendations['ID'][1][ugettext('Educación emocional')][5][ugettext('Resolución de conflictos')][ugettext('Grupo')].append(ugettext('El índice de disociación (ID) es alto.'))
            recommendations['ID'][1][ugettext('Educación emocional')][5][ugettext('Resolución de conflictos')][ugettext('Grupo')].append(ugettext('Se recomienda trabajar esta categoría en grupos donde se observen configuraciones sociométricas de grupos o islas enfrentadas.'))


            if ugettext('Grupo') not in recommendations['ID'][3][ugettext('Grupo y aula')][1][ugettext('Cohesión de grupo')]:
                recommendations['ID'][3][ugettext('Grupo y aula')][1][ugettext('Cohesión de grupo')][ugettext('Grupo')] = []
                recommendations['ID'][3][ugettext('Grupo y aula')][1][ugettext('Cohesión de grupo')][ugettext('Grupo')].append(URL + etapa +"/" + Link.objects.get(name="Grupo y aula").url + "/" + etapa.split('_')[1] + "_" + Link.objects.get(name="Cohesión de grupo").url + '.php')
            recommendations['ID'][3][ugettext('Grupo y aula')][1][ugettext('Cohesión de grupo')][ugettext('Grupo')].append(ugettext('El índice de disociación (ID) es alto'))
            recommendations['ID'][3][ugettext('Grupo y aula')][1][ugettext('Cohesión de grupo')][ugettext('Grupo')].append(ugettext('Se recomienda trabajar esta categoría en grupos donde los rechazos puedan estar motivados por falta de confianza.'))

            if ugettext('Grupo') not in recommendations['ID'][3][ugettext('Grupo y aula')][3][ugettext('Trabajo colaborativo y cooperativo')]:
                recommendations['ID'][3][ugettext('Grupo y aula')][3][ugettext('Trabajo colaborativo y cooperativo')][ugettext('Grupo')] = []
                recommendations['ID'][3][ugettext('Grupo y aula')][3][ugettext('Trabajo colaborativo y cooperativo')][ugettext('Grupo')].append(URL + etapa +"/" + Link.objects.get(name="Grupo y aula").url + "/" + etapa.split('_')[1] + "_" + Link.objects.get(name="Trabajo colaborativo y cooperativo").url + '.php')
            recommendations['ID'][3][ugettext('Grupo y aula')][3][ugettext('Trabajo colaborativo y cooperativo')][ugettext('Grupo')].append(ugettext('El índice de disociación (ID) es alto.'))
            recommendations['ID'][3][ugettext('Grupo y aula')][3][ugettext('Trabajo colaborativo y cooperativo')][ugettext('Grupo')].append(ugettext('Se recomienda trabajar esta categoría en grupos donde se observen configuraciones sociométricas de grupos enfrentados.'))

            if ugettext('Grupo') not in recommendations['ID'][2][ugettext('Educación en valores')][2][ugettext('Solidaridad')]:
                recommendations['ID'][2][ugettext('Educación en valores')][2][ugettext('Solidaridad')][ugettext('Grupo')] = []
                recommendations['ID'][2][ugettext('Educación en valores')][2][ugettext('Solidaridad')][ugettext('Grupo')].append(URL + etapa +"/" + Link.objects.get(name="Educación en valores").url + "/" + etapa.split('_')[1] + "_" + Link.objects.get(name="Solidaridad").url + '.php')
            recommendations['ID'][2][ugettext('Educación en valores')][2][ugettext('Solidaridad')][ugettext('Grupo')].append(ugettext('El índice de disociación (ID) es alto.'))
            recommendations['ID'][2][ugettext('Educación en valores')][2][ugettext('Solidaridad')][ugettext('Grupo')].append(ugettext('Se recomienda trabajar esta categoría en grupos en los que puedan existir desequilibrios socioeconómicos.'))

            if ugettext('Grupo') not in recommendations['ID'][2][ugettext('Educación en valores')][1][ugettext('Interculturalidad')]:
                recommendations["ID"][2][ugettext('Educación en valores')][1][ugettext('Interculturalidad')][ugettext('Grupo')] = []
                recommendations["ID"][2][ugettext('Educación en valores')][1][ugettext('Interculturalidad')][ugettext('Grupo')].append(URL + etapa +"/" + Link.objects.get(name="Educación en valores").url + "/" + etapa.split('_')[1] + "_" + Link.objects.get(name="Interculturalidad").url + '.php')
            recommendations["ID"][2][ugettext('Educación en valores')][1][ugettext('Interculturalidad')][ugettext('Grupo')].append(ugettext('El índice de disociación (ID) es alto.'))
            recommendations["ID"][2][ugettext('Educación en valores')][1][ugettext('Interculturalidad')][ugettext('Grupo')].append(ugettext('Se recomienda trabajar esta categoría en grupos en los que se dé la circunstancia de la multiculturalidad (raza, etnia, religión, etc.).'))


    if alumnoCurrent != '':
        spValue = {alumnoCurrent: spValue[alumnoCurrent]}
    othersDone = {}
    for user in spValue:
        studentName = AlumnoTests.objects.get(username=user)

        if spValue[user][list(spValue[user])[0]] == ugettext("Bajo") and npValue[user][list(npValue[user])[0]] == ugettext("Bajo"):
            # if ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y el grupo ") not in recommendations["SP"][2][ugettext('Grupo y aula')][1][ugettext('Cohesión de grupo')]:
            #     recommendations["SP"][2][ugettext('Grupo y aula')][1][ugettext('Cohesión de grupo')][ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y el grupo ")] = []
            #     recommendations["SP"][2][ugettext('Grupo y aula')][1][ugettext('Cohesión de grupo')][ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y el grupo ")].append(URL + etapa +"/" + Link.objects.get(name="Grupo y aula").url + "/" + etapa.split('_')[1] + "_" + Link.objects.get(name="Cohesión de grupo").url + '.php')
            #     # recommendations["SP"][2][ugettext('Grupo y aula')][1][ugettext('Cohesión de grupo')][ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y el grupo ")].append(int(studentName.username))
            # recommendations["SP"][2][ugettext('Grupo y aula')][1][ugettext('Cohesión de grupo')][ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y el grupo ")].append(ugettext('Su estatus de elecciones positivas (SP) y su nivel medio de popularidad (NP) son bajos.'))
            # recommendations["SP"][2][ugettext('Grupo y aula')][1][ugettext('Cohesión de grupo')][ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y el grupo ")].append(ugettext(''))

            # if ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y el grupo ") not in recommendations["SP"][2][ugettext('Grupo y aula')][3][ugettext('Trabajo colaborativo y cooperativo')]:
            #     recommendations["SP"][2][ugettext('Grupo y aula')][3][ugettext('Trabajo colaborativo y cooperativo')][ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y el grupo ")] = []
            #     recommendations["SP"][2][ugettext('Grupo y aula')][3][ugettext('Trabajo colaborativo y cooperativo')][ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y el grupo ")].append(URL + etapa +"/" + Link.objects.get(name="Grupo y aula").url + "/" + etapa.split('_')[1] + "_" + Link.objects.get(name="Trabajo colaborativo y cooperativo").url + '.php')
            #     # recommendations["SP"][2][ugettext('Grupo y aula')][3][ugettext('Trabajo colaborativo y cooperativo')][ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y el grupo ")].append(int(studentName.username))
            # recommendations["SP"][2][ugettext('Grupo y aula')][3][ugettext('Trabajo colaborativo y cooperativo')][ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y el grupo ")].append(ugettext('Su estatus de elecciones positivas (SP) y su nivel medio de popularidad (NP) son bajos.'))
            # recommendations["SP"][2][ugettext('Grupo y aula')][3][ugettext('Trabajo colaborativo y cooperativo')][ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y el grupo ")].append(ugettext(''))

            if ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y el grupo ") not in recommendations["SP"][1][ugettext('Educación en valores')][1][ugettext('Interculturalidad')]:
                recommendations["SP"][1][ugettext('Educación en valores')][1][ugettext('Interculturalidad')][ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y el grupo ")] = []
                recommendations["SP"][1][ugettext('Educación en valores')][1][ugettext('Interculturalidad')][ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y el grupo ")].append(URL + etapa +"/" + Link.objects.get(name="Educación en valores").url + "/" + etapa.split('_')[1] + "_" + Link.objects.get(name="Interculturalidad").url + '.php')
                # recommendations["SP"][1][ugettext('Educación en valores')][1][ugettext('Interculturalidad')][ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y el grupo ")].append(int(studentName.username))
            recommendations["SP"][1][ugettext('Educación en valores')][1][ugettext('Interculturalidad')][ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y el grupo ")].append(ugettext('Su estatus de elecciones positivas (SP) y su nivel medio de popularidad (NP) son bajos.'))
            recommendations["SP"][1][ugettext('Educación en valores')][1][ugettext('Interculturalidad')][ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y el grupo ")].append(ugettext('Cuando se dé la circunstancia de la multiculturalidad (raza, etnia, religión, etc.)'))

            if ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y el grupo ") not in recommendations["SP"][1][ugettext('Educación en valores')][2][ugettext('Respeto y tolerancia')]:
                recommendations["SP"][1][ugettext('Educación en valores')][2][ugettext('Respeto y tolerancia')][ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y el grupo ")] = []
                recommendations["SP"][1][ugettext('Educación en valores')][2][ugettext('Respeto y tolerancia')][ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y el grupo ")].append(URL + etapa +"/" + Link.objects.get(name="Educación en valores").url + "/" + etapa.split('_')[1] + "_" + Link.objects.get(name="Respeto y tolerancia").url + '.php')
                # recommendations["SP"][1][ugettext('Educación en valores')][2][ugettext('Respeto y tolerancia')][ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y el grupo ")].append(int(studentName.username))
            recommendations["SP"][1][ugettext('Educación en valores')][2][ugettext('Respeto y tolerancia')][ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y el grupo ")].append(ugettext('Su estatus de elecciones positivas (SP) y su nivel medio de popularidad (NP) son bajos.'))
            recommendations["SP"][1][ugettext('Educación en valores')][2][ugettext('Respeto y tolerancia')][ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y el grupo ")].append(ugettext('Cuando se den las circunstancias de diversidad funcional o singularidad física o psíquica, identidad de género, diferencias socioeconómicas, etc.'))

        if user in ppValue and user in papValue:
            if ppValue[user][list(ppValue[user])[0]] == ugettext("Bajo") and papValue[user][list(papValue[user])[0]] == ugettext("Alto"):

                if ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y el grupo ") not in recommendations['PP'][3][ugettext('Grupo y aula')][1][ugettext('Cohesión de grupo')]:
                    recommendations['PP'][3][ugettext('Grupo y aula')][1][ugettext('Cohesión de grupo')][ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y el grupo ")] = []
                    recommendations['PP'][3][ugettext('Grupo y aula')][1][ugettext('Cohesión de grupo')][ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y el grupo ")].append(URL + etapa +"/" + Link.objects.get(name="Grupo y aula").url + "/" + etapa.split('_')[1] + "_" + Link.objects.get(name="Cohesión de grupo").url + '.php')
                    # recommendations['PP'][3][ugettext('Grupo y aula')][1][ugettext('Cohesión de grupo')][ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y el grupo ")].append(int(studentName.username))
                recommendations['PP'][3][ugettext('Grupo y aula')][1][ugettext('Cohesión de grupo')][ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y el grupo ")].append(ugettext('El número de compañeros por los que se cree elegido (PP) es bajo y su percepción acertada de ese número (PAP) es alta.'))
                recommendations['PP'][3][ugettext('Grupo y aula')][1][ugettext('Cohesión de grupo')][ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y el grupo ")].append(ugettext('Se dé la circunstancia de ser un alumno de nueva incorporación o desconocido para el grupo.'))

                if ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y el grupo ") not in recommendations['PP'][3][ugettext('Grupo y aula')][3][ugettext('Trabajo colaborativo y cooperativo')]:
                    recommendations['PP'][3][ugettext('Grupo y aula')][3][ugettext('Trabajo colaborativo y cooperativo')][ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y el grupo ")] = []
                    recommendations['PP'][3][ugettext('Grupo y aula')][3][ugettext('Trabajo colaborativo y cooperativo')][ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y el grupo ")].append(URL + etapa +"/" + Link.objects.get(name="Grupo y aula").url + "/" + etapa.split('_')[1] + "_" + Link.objects.get(name="Trabajo colaborativo y cooperativo").url + '.php')
                    # recommendations['PP'][3][ugettext('Grupo y aula')][3][ugettext('Trabajo colaborativo y cooperativo')][ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y el grupo ")].append(int(studentName.username))
                recommendations['PP'][3][ugettext('Grupo y aula')][3][ugettext('Trabajo colaborativo y cooperativo')][ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y el grupo ")].append(ugettext('El número de compañeros por los que se cree elegido (PP) es bajo y su percepción acertada de ese número (PAP) es alta en preguntas de ámbito formal.'))
                recommendations['PP'][3][ugettext('Grupo y aula')][3][ugettext('Trabajo colaborativo y cooperativo')][ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y el grupo ")].append(ugettext(''))

                if studentName.get_nombre() + " "  + studentName.get_apellidos() not in recommendations["PP"][2][ugettext('Educación en valores')][4][ugettext('Responsabilidad')]:
                    recommendations["PP"][2][ugettext('Educación en valores')][4][ugettext('Responsabilidad')][studentName.get_nombre() + " "  + studentName.get_apellidos()] = []
                    recommendations["PP"][2][ugettext('Educación en valores')][4][ugettext('Responsabilidad')][studentName.get_nombre() + " "  + studentName.get_apellidos()].append(URL + etapa +"/" + Link.objects.get(name="Educación en valores").url + "/" + etapa.split('_')[1] + "_" + Link.objects.get(name="Responsabilidad").url + '.php')
                    # recommendations['PP'][2][ugettext('Educación en valores')][4][ugettext('Responsabilidad')][studentName.get_nombre() + " "  + studentName.get_apellidos()].append(int(studentName.username))
                recommendations["PP"][2][ugettext('Educación en valores')][4][ugettext('Responsabilidad')][studentName.get_nombre() + " "  + studentName.get_apellidos()].append(ugettext('El número de compañeros por los que se cree elegido (PP) es bajo y su percepción acertada de ese número (PAP) es alta en preguntas de ámbito formal.'))
                recommendations["PP"][2][ugettext('Educación en valores')][4][ugettext('Responsabilidad')][studentName.get_nombre() + " "  + studentName.get_apellidos()].append(ugettext(''))


            if ppValue[user][list(ppValue[user])[0]] == ugettext("Bajo") and papValue[user][list(papValue[user])[0]] == ugettext("Bajo"):
                if studentName.get_nombre() + " "  + studentName.get_apellidos() not in recommendations['PP'][1][ugettext('Educación emocional')][1][ugettext('Autoconcepto y autoestima')]:
                    recommendations['PP'][1][ugettext('Educación emocional')][1][ugettext('Autoconcepto y autoestima')][studentName.get_nombre() + " "  + studentName.get_apellidos()] = []
                    recommendations['PP'][1][ugettext('Educación emocional')][1][ugettext('Autoconcepto y autoestima')][studentName.get_nombre() + " "  + studentName.get_apellidos()].append(URL + etapa +"/" + Link.objects.get(name="Educación emocional").url + "/" + etapa.split('_')[1] + "_" + Link.objects.get(name="Autoconcepto y autoestima").url + '.php')
                    # recommendations['PP'][1][ugettext('Educación emocional')][1][ugettext('Autoconcepto y autoestima')][studentName.get_nombre() + " "  + studentName.get_apellidos()].append(int(studentName.username))
                recommendations['PP'][1][ugettext('Educación emocional')][1][ugettext('Autoconcepto y autoestima')][studentName.get_nombre() + " "  + studentName.get_apellidos()].append(ugettext('El número de compañeros por los que se cree elegido (PP) es bajo y su percepción acertada de ese número (PAP) es baja.'))
                recommendations['PP'][1][ugettext('Educación emocional')][1][ugettext('Autoconcepto y autoestima')][studentName.get_nombre() + " "  + studentName.get_apellidos()].append(ugettext(''))


        if user in rpValue:
            if rpValue[user][list(rpValue[user])[0]] == "Cero":
                if studentName.get_nombre() + " "  + studentName.get_apellidos() not in recommendations["RP"][1][ugettext('Educación emocional')][1][ugettext('Autoconcepto y autoestima')]:
                    recommendations["RP"][1][ugettext('Educación emocional')][1][ugettext('Autoconcepto y autoestima')][studentName.get_nombre() + " "  + studentName.get_apellidos()] = []
                    recommendations["RP"][1][ugettext('Educación emocional')][1][ugettext('Autoconcepto y autoestima')][studentName.get_nombre() + " "  + studentName.get_apellidos()].append(URL + etapa +"/" + Link.objects.get(name="Educación emocional").url + "/" + etapa.split('_')[1] + "_" + Link.objects.get(name="Autoconcepto y autoestima").url + '.php')
                    # recommendations["RP"][1][ugettext('Educación emocional')][1][ugettext('Autoconcepto y autoestima')][studentName.get_nombre() + " "  + studentName.get_apellidos()].append(int(studentName.username))
                recommendations["RP"][1][ugettext('Educación emocional')][1][ugettext('Autoconcepto y autoestima')][studentName.get_nombre() + " "  + studentName.get_apellidos()].append(ugettext('No tiene elecciones recíprocas positivas (RP) o amistades.'))
                recommendations["RP"][1][ugettext('Educación emocional')][1][ugettext('Autoconcepto y autoestima')][studentName.get_nombre() + " "  + studentName.get_apellidos()].append(ugettext('Cuando un alumno no tiene amistades (RP) se debe potenciar las cualidades positivas del alumno en el grupo.'))

                if studentName.get_nombre() + " "  + studentName.get_apellidos() not in recommendations['RP'][2][ugettext('Grupo y aula')][1][ugettext('Cohesión de grupo')]: #NO TABLA
                    recommendations['RP'][2][ugettext('Grupo y aula')][1][ugettext('Cohesión de grupo')][ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y el grupo ")] = []
                    recommendations['RP'][2][ugettext('Grupo y aula')][1][ugettext('Cohesión de grupo')][ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y el grupo ")].append(URL + etapa +"/" + Link.objects.get(name="Grupo y aula").url + "/" + etapa.split('_')[1] + "_" + Link.objects.get(name="Cohesión de grupo").url + '.php')
                    # recommendations['RP'][2][ugettext('Grupo y aula')][1][ugettext('Cohesión de grupo')][ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y el grupo ")].append(int(studentName.username))
                recommendations['RP'][2][ugettext('Grupo y aula')][1][ugettext('Cohesión de grupo')][ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y el grupo ")].append(ugettext('No tiene elecciones recíprocas positivas (RP) o amistades.'))
                recommendations['RP'][2][ugettext('Grupo y aula')][1][ugettext('Cohesión de grupo')][ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y el grupo ")].append(ugettext('Cuando un alumno no tiene amistades (RP) y se dé la circunstancia de ser un alumno de nueva incorporación o tenga una personalidad introvertida, puede tener una posición sociométrica de aislado o marginado.'))


        if user in pnValue and user in panValue:
            if pnValue[user][list(pnValue[user])[0]] == ugettext("Alto") and panValue[user][list(panValue[user])[0]] == ugettext("Bajo"):
                if studentName.get_nombre() + " "  + studentName.get_apellidos() not in recommendations["PN"][1][ugettext('Educación emocional')][1][ugettext('Autoconcepto y autoestima')]:
                    recommendations["PN"][1][ugettext('Educación emocional')][1][ugettext('Autoconcepto y autoestima')][studentName.get_nombre() + " "  + studentName.get_apellidos()] = []
                    recommendations["PN"][1][ugettext('Educación emocional')][1][ugettext('Autoconcepto y autoestima')][studentName.get_nombre() + " "  + studentName.get_apellidos()].append(URL + etapa +"/" + Link.objects.get(name="Educación emocional").url + "/" + etapa.split('_')[1] + "_" + Link.objects.get(name="Autoconcepto y autoestima").url + '.php')
                    # recommendations["PN"][1][ugettext('Educación emocional')][1][ugettext('Autoconcepto y autoestima')][studentName.get_nombre() + " "  + studentName.get_apellidos()].append(int(studentName.username))
                recommendations["PN"][1][ugettext('Educación emocional')][1][ugettext('Autoconcepto y autoestima')][studentName.get_nombre() + " "  + studentName.get_apellidos()].append(ugettext('El número de compañeros por los que se cree rechazado o percepción negativa (PN) es alta y su percepción acertada de ese número (PAN) es baja.'))
                recommendations["PN"][1][ugettext('Educación emocional')][1][ugettext('Autoconcepto y autoestima')][studentName.get_nombre() + " "  + studentName.get_apellidos()].append(ugettext(''))

            if pnValue[user][list(pnValue[user])[0]] == ugettext("Alto") and panValue[user][list(panValue[user])[0]] == ugettext("Alto"):
                if studentName.get_nombre() + " "  + studentName.get_apellidos() not in recommendations["PN"][1][ugettext('Educación emocional')][2][ugettext('Autoregulación')]:
                    recommendations["PN"][1][ugettext('Educación emocional')][2][ugettext('Autoregulación')][studentName.get_nombre() + " "  + studentName.get_apellidos()] = []
                    recommendations["PN"][1][ugettext('Educación emocional')][2][ugettext('Autoregulación')][studentName.get_nombre() + " "  + studentName.get_apellidos()].append(URL + etapa +"/" + Link.objects.get(name="Educación emocional").url + "/" + etapa.split('_')[1] + "_" + Link.objects.get(name="Autoregulación").url + '.php')
                    # recommendations["PN"][1][ugettext('Educación emocional')][2][ugettext('Autoregulación')][studentName.get_nombre() + " "  + studentName.get_apellidos()].append(int(studentName.username))
                recommendations["PN"][1][ugettext('Educación emocional')][2][ugettext('Autoregulación')][studentName.get_nombre() + " "  + studentName.get_apellidos()].append(ugettext('El número de compañeros por los que se cree rechazado o percepción negativa (PN) es alta y su percepción acertada de ese número (PAN) es alta, motivado en cuestiones de conducta molesta.'))
                recommendations["PN"][1][ugettext('Educación emocional')][2][ugettext('Autoregulación')][studentName.get_nombre() + " "  + studentName.get_apellidos()].append(ugettext(''))


        if ipnValue[user][list(ipnValue[user])[0]] == ugettext("Alto"):
            if studentName.get_nombre() + " "  + studentName.get_apellidos() not in recommendations["IPN"][1][ugettext('Educación emocional')][1][ugettext('Autoconcepto y autoestima')]:
                recommendations["IPN"][1][ugettext('Educación emocional')][1][ugettext('Autoconcepto y autoestima')][studentName.get_nombre() + " "  + studentName.get_apellidos()] = []
                recommendations["IPN"][1][ugettext('Educación emocional')][1][ugettext('Autoconcepto y autoestima')][studentName.get_nombre() + " "  + studentName.get_apellidos()].append(URL + etapa +"/" + Link.objects.get(name="Educación emocional").url + "/" + etapa.split('_')[1] + "_" + Link.objects.get(name="Autoconcepto y autoestima").url + '.php')
                # recommendations["IPN"][1][ugettext('Educación emocional')][1][ugettext('Autoconcepto y autoestima')][studentName.get_nombre() + " "  + studentName.get_apellidos()].append(int(studentName.username))
            recommendations["IPN"][1][ugettext('Educación emocional')][1][ugettext('Autoconcepto y autoestima')][studentName.get_nombre() + " "  + studentName.get_apellidos()].append(ugettext('La cantidad de veces que es nombrado/a por sus compañeros en las categorías de carácter negativo o el índice de preferencia social negativa (IPN) es alto.'))
            recommendations["IPN"][1][ugettext('Educación emocional')][1][ugettext('Autoconcepto y autoestima')][studentName.get_nombre() + " "  + studentName.get_apellidos()].append(ugettext('Cuando el índice afecta al atributo de "triste" o similar.'))

            if studentName.get_nombre() + " "  + studentName.get_apellidos() not in recommendations["IPN"][1][ugettext('Educación emocional')][2][ugettext('Autoregulación')]:
                recommendations["IPN"][1][ugettext('Educación emocional')][2][ugettext('Autoregulación')][studentName.get_nombre() + " "  + studentName.get_apellidos()] = []
                recommendations["IPN"][1][ugettext('Educación emocional')][2][ugettext('Autoregulación')][studentName.get_nombre() + " "  + studentName.get_apellidos()].append(URL + etapa +"/" + Link.objects.get(name="Educación emocional").url + "/" + etapa.split('_')[1] + "_" + Link.objects.get(name="Autoregulación").url + '.php')
                # recommendations["IPN"][1][ugettext('Educación emocional')][2][ugettext('Autoregulación')][studentName.get_nombre() + " "  + studentName.get_apellidos()].append(int(studentName.username))
            recommendations["IPN"][1][ugettext('Educación emocional')][2][ugettext('Autoregulación')][studentName.get_nombre() + " "  + studentName.get_apellidos()].append(ugettext('La cantidad de veces que es nombrado/a por sus compañeros en las categorías de carácter negativo o el índice de preferencia social negativa (IPN) es alto.'))
            recommendations["IPN"][1][ugettext('Educación emocional')][2][ugettext('Autoregulación')][studentName.get_nombre() + " "  + studentName.get_apellidos()].append(ugettext('Cuando el índice afecta al atributo de "molestar" o similar.'))

            if studentName.get_nombre() + " "  + studentName.get_apellidos() not in recommendations["IPN"][1][ugettext('Educación emocional')][3][ugettext('Habilidades sociales')]:
                recommendations["IPN"][1][ugettext('Educación emocional')][3][ugettext('Habilidades sociales')][studentName.get_nombre() + " "  + studentName.get_apellidos()] = []
                recommendations["IPN"][1][ugettext('Educación emocional')][3][ugettext('Habilidades sociales')][studentName.get_nombre() + " "  + studentName.get_apellidos()].append(URL + etapa +"/" + Link.objects.get(name="Educación emocional").url + "/" + etapa.split('_')[1] + "_" + Link.objects.get(name="Habilidades sociales").url + '.php')
                # recommendations["IPN"][1][ugettext('Educación emocional')][3][ugettext('Habilidades sociales')][studentName.get_nombre() + " "  + studentName.get_apellidos()].append(int(studentName.username))
            recommendations["IPN"][1][ugettext('Educación emocional')][3][ugettext('Habilidades sociales')][studentName.get_nombre() + " "  + studentName.get_apellidos()].append(ugettext('La cantidad de veces que es nombrado/a por sus compañeros en las categorías de carácter negativo o el índice de preferencia social negativa (IPN) es alto.'))
            recommendations["IPN"][1][ugettext('Educación emocional')][3][ugettext('Habilidades sociales')][studentName.get_nombre() + " "  + studentName.get_apellidos()].append(ugettext('Cuando el índice afecta al atributo de "pesado" o similar.'))


        if snValue[user][list(snValue[user])[0]] == ugettext("Alto") and nnValue[user][list(nnValue[user])[0]] == ugettext("Alto"):
            if studentName.get_nombre() + " "  + studentName.get_apellidos() not in recommendations["SN"][1][ugettext('Educación emocional')][2][ugettext('Autoregulación')]:
                recommendations["SN"][1][ugettext('Educación emocional')][2][ugettext('Autoregulación')][studentName.get_nombre() + " "  + studentName.get_apellidos()] = []
                recommendations["SN"][1][ugettext('Educación emocional')][2][ugettext('Autoregulación')][studentName.get_nombre() + " "  + studentName.get_apellidos()].append(URL + etapa +"/" + Link.objects.get(name="Educación emocional").url + "/" + etapa.split('_')[1] + "_" + Link.objects.get(name="Autoregulación").url + '.php')
                # recommendations["SN"][1][ugettext('Educación emocional')][2][ugettext('Autoregulación')][studentName.get_nombre() + " "  + studentName.get_apellidos()].append(int(studentName.username))
            recommendations["SN"][1][ugettext('Educación emocional')][2][ugettext('Autoregulación')][studentName.get_nombre() + " "  + studentName.get_apellidos()].append(ugettext('Su estatus de eleccions negativas (SN) y su nivel medio de rechazo (NN) son altos'))
            recommendations["SN"][1][ugettext('Educación emocional')][2][ugettext('Autoregulación')][studentName.get_nombre() + " "  + studentName.get_apellidos()].append(ugettext('Alumnado con posiciones sociométricas de rechazado parcial o total y con índice de rechazo (SN) alto en el que las respuestas al “por qué” del rechazo sean similares a “porque me molesta”  y cuestiones de molestia acerca de su conducta.'))

        if ipValue[user][list(ipValue[user])[0]] == ugettext("Bajo") and impValue[user][list(impValue[user])[0]] == ugettext("Bajo"):
            if studentName.get_nombre() + " "  + studentName.get_apellidos() not in recommendations["IP"][1][ugettext('Educación emocional')][3][ugettext('Habilidades sociales')]:
                recommendations["IP"][1][ugettext('Educación emocional')][3][ugettext('Habilidades sociales')][studentName.get_nombre() + " "  + studentName.get_apellidos()] = []
                recommendations["IP"][1][ugettext('Educación emocional')][3][ugettext('Habilidades sociales')][studentName.get_nombre() + " "  + studentName.get_apellidos()].append(URL + etapa +"/" + Link.objects.get(name="Educación emocional").url + "/" + etapa.split('_')[1] + "_" + Link.objects.get(name="Habilidades sociales").url + '.php')
                # recommendations["IP"][1][ugettext('Educación emocional')][3][ugettext('Habilidades sociales')][studentName.get_nombre() + " "  + studentName.get_apellidos()].append(int(studentName.username))
            recommendations["IP"][1][ugettext('Educación emocional')][3][ugettext('Habilidades sociales')][studentName.get_nombre() + " "  + studentName.get_apellidos()].append(ugettext('El número de compañeros que se creen elegidos por él/ella o su impresión positiva (IP) es baja y el nivel medio de impresión que tiene el grupo de ser elegido por él/ella (IMP) es bajo'))
            recommendations["IP"][1][ugettext('Educación emocional')][3][ugettext('Habilidades sociales')][studentName.get_nombre() + " "  + studentName.get_apellidos()].append(ugettext('El grupo no se cree escogido por el alumno o alumna.'))

        if user in oinValue:
            if len(oinValue[user]) > 0:

                otherStudents = ''
                reasons = ''
                if len(oinValue[user]) > 0:
                    for r in oinValue[user]:
                        o = AlumnoTests.objects.get(username=r)
                        if otherStudents == '':
                            otherStudents += o.get_nombre() + " " + o.get_apellidos()
                        else:
                            otherStudents += "/" + o.get_nombre() + " " + o.get_apellidos()
                        if alumnoCurrent != '':
                            reasons += o.get_nombre() + " " + o.get_apellidos() + ugettext(' lo/la elige')
                    if otherStudents != '':

                        if studentName.get_nombre() + " "  + studentName.get_apellidos() not in recommendations["OIN"][1][ugettext('Educación emocional')][1][ugettext('Autoconcepto y autoestima')]:
                            recommendations["OIN"][1][ugettext('Educación emocional')][1][ugettext('Autoconcepto y autoestima')][studentName.get_nombre() + " "  + studentName.get_apellidos()] = []
                            recommendations["OIN"][1][ugettext('Educación emocional')][1][ugettext('Autoconcepto y autoestima')][studentName.get_nombre() + " "  + studentName.get_apellidos()].append(URL + etapa +"/" + Link.objects.get(name="Educación emocional").url + "/" + etapa.split('_')[1] + "_" + Link.objects.get(name="Autoconcepto y autoestima").url + '.php')
                            # recommendations["OIN"][1][ugettext('Educación emocional')][1][ugettext('Autoconcepto y autoestima')][studentName.get_nombre() + " "  + studentName.get_apellidos()].append(int(studentName.username))
                        recommendations["OIN"][1][ugettext('Educación emocional')][1][ugettext('Autoconcepto y autoestima')][studentName.get_nombre() + " "  + studentName.get_apellidos()].append(ugettext('Contradicción entre la expectativa de ser rechazado por determinados compañeros o compañeras cuando en realidad han sido elegidos por ellos'))
                        recommendations["OIN"][1][ugettext('Educación emocional')][1][ugettext('Autoconcepto y autoestima')][studentName.get_nombre() + " "  + studentName.get_apellidos()].append(reasons + ugettext(" cuando el pensaba ser rechazado/a."))


        if user in epValue:
            if epValue[user][list(epValue[user])[0]] == ugettext("Bajo"):
                if ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y el grupo ") not in recommendations["EP"][3][ugettext('Grupo y aula')][1][ugettext('Cohesión de grupo')]:
                    recommendations["EP"][3][ugettext('Grupo y aula')][1][ugettext('Cohesión de grupo')][ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y el grupo ")] = []
                    recommendations["EP"][3][ugettext('Grupo y aula')][1][ugettext('Cohesión de grupo')][ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y el grupo ")].append(URL + etapa +"/" + Link.objects.get(name="Grupo y aula").url + "/" + etapa.split('_')[1] + "_" + Link.objects.get(name="Cohesión de grupo").url + '.php')
                    # recommendations["EP"][3][ugettext('Grupo y aula')][1][ugettext('Cohesión de grupo')][ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y el grupo ")].append(int(studentName.username))
                recommendations["EP"][3][ugettext('Grupo y aula')][1][ugettext('Cohesión de grupo')][ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y el grupo ")].append(ugettext('La suma de sus elecciones positivas o expansividad positiva (EP) es baja'))
                recommendations["EP"][3][ugettext('Grupo y aula')][1][ugettext('Cohesión de grupo')][ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y el grupo ")].append(ugettext('Si se da la circunstancia de ser un alumno de nueva incorporación.'))

                if ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y el grupo ") not in recommendations["EP"][3][ugettext('Grupo y aula')][3][ugettext('Trabajo colaborativo y cooperativo')]:
                    recommendations["EP"][3][ugettext('Grupo y aula')][3][ugettext('Trabajo colaborativo y cooperativo')][ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y el grupo ")] = []
                    recommendations["EP"][3][ugettext('Grupo y aula')][3][ugettext('Trabajo colaborativo y cooperativo')][ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y el grupo ")].append(URL + etapa +"/" + Link.objects.get(name="Grupo y aula").url + "/" + etapa.split('_')[1] + "_" + Link.objects.get(name="Trabajo colaborativo y cooperativo").url + '.php')
                    # recommendations["EP"][3][ugettext('Grupo y aula')][3][ugettext('Trabajo colaborativo y cooperativo')][ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y el grupo ")].append(int(studentName.username))
                recommendations["EP"][3][ugettext('Grupo y aula')][3][ugettext('Trabajo colaborativo y cooperativo')][ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y el grupo ")].append(ugettext('La suma de sus elecciones positivas o expansividad positiva (EP) es baja'))
                recommendations["EP"][3][ugettext('Grupo y aula')][3][ugettext('Trabajo colaborativo y cooperativo')][ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y el grupo ")].append(ugettext(''))

                if ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y el grupo ") not in recommendations["EP"][1][ugettext('Educación emocional')][4][ugettext('Empatía')]:
                    recommendations["EP"][1][ugettext('Educación emocional')][4][ugettext('Empatía')][ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y el grupo ")] = []
                    recommendations["EP"][1][ugettext('Educación emocional')][4][ugettext('Empatía')][ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y el grupo ")].append(URL + etapa +"/" + Link.objects.get(name="Educación emocional").url + "/" + etapa.split('_')[1] + "_" + Link.objects.get(name="Empatía").url + '.php')
                    # recommendations["EP"][1][ugettext('Educación emocional')][4][ugettext('Empatía')][ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y el grupo ")].append(int(studentName.username))
                recommendations["EP"][1][ugettext('Educación emocional')][4][ugettext('Empatía')][ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y el grupo ")].append(ugettext('La suma de sus elecciones positivas o expansividad positiva (EP) es baja'))
                recommendations["EP"][1][ugettext('Educación emocional')][4][ugettext('Empatía')][ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y el grupo ")].append(ugettext('Puede tener una posición sociométrica de solitario.'))

                if ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y el grupo ") not in recommendations["EP"][2][ugettext('Educación en valores')][2][ugettext('Respeto y tolerancia')]:
                    recommendations["EP"][2][ugettext('Educación en valores')][2][ugettext('Respeto y tolerancia')][ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y el grupo ")] = []
                    recommendations["EP"][2][ugettext('Educación en valores')][2][ugettext('Respeto y tolerancia')][ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y el grupo ")].append(URL + etapa +"/" + Link.objects.get(name="Educación en valores").url + "/" + etapa.split('_')[1] + "_" + Link.objects.get(name="Respeto y tolerancia").url + '.php')
                    # recommendations["EP"][2][ugettext('Educación en valores')][2][ugettext('Respeto y tolerancia')][ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y el grupo ")].append(int(studentName.username))
                recommendations["EP"][2][ugettext('Educación en valores')][2][ugettext('Respeto y tolerancia')][ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y el grupo ")].append(ugettext('La suma de sus elecciones positivas o expansividad positiva (EP) es baja'))
                recommendations["EP"][2][ugettext('Educación en valores')][2][ugettext('Respeto y tolerancia')][ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y el grupo ")].append(ugettext('Si se dan las circunstancias de diversidad funcional o singularidad física o psíquica, identidad de género, diferencias socioeconómicas, etc. en él o en su entorno.'))

        if user in enValue:
            otherStudents = ''
            reasons = ''
            if enValue[user][list(enValue[user])[0]] == ugettext("Alto"):
                for r in matrix[2][user]:
                    o = AlumnoTests.objects.get(username=r)
                    if otherStudents == '':
                        otherStudents += o.get_nombre() + " " + o.get_apellidos()
                    else:
                        otherStudents += "/" + o.get_nombre() + " " + o.get_apellidos()
                    if alumnoCurrent != '':
                        if r in matrixText[2][user]:
                            if matrixText[2][user][r] != '':
                                reasons += ugettext('Rechaza a ') + o.get_nombre() + " " + o.get_apellidos() + ugettext(' por el motivo "') + matrixText[2][user][r] + '". '
                            else:
                                reasons += ugettext('Rechaza a ') + o.get_nombre() + " " + o.get_apellidos() + '. '
                if otherStudents != '':

                    if ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y ") + otherStudents not in recommendations["EN"][1][ugettext('Educación emocional')][4][ugettext('Empatía')]:
                        recommendations["EN"][1][ugettext('Educación emocional')][4][ugettext('Empatía')][ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y ") + otherStudents] = []
                        recommendations["EN"][1][ugettext('Educación emocional')][4][ugettext('Empatía')][ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y ") + otherStudents].append(URL + etapa +"/" + Link.objects.get(name="Educación emocional").url + "/" + etapa.split('_')[1] + "_" + Link.objects.get(name="Empatía").url + '.php')
                    recommendations["EN"][1][ugettext('Educación emocional')][4][ugettext('Empatía')][ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y ") + otherStudents].append(ugettext('La suma de sus elecciones negativas o su expansividad negativa (EN) es alta') + ". " )
                    recommendations["EN"][1][ugettext('Educación emocional')][4][ugettext('Empatía')][ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y ") + otherStudents].append(reasons)

                    if ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y ") + otherStudents not in recommendations["EN"][2][ugettext('Educación en valores')][2][ugettext('Respeto y tolerancia')]:
                        recommendations["EN"][2][ugettext('Educación en valores')][2][ugettext('Respeto y tolerancia')][ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y ") + otherStudents] = []
                        recommendations["EN"][2][ugettext('Educación en valores')][2][ugettext('Respeto y tolerancia')][ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y ") + otherStudents].append(URL + etapa +"/" + Link.objects.get(name="Educación en valores").url + "/" + etapa.split('_')[1] + "_" + Link.objects.get(name="Respeto y tolerancia").url + '.php')
                    recommendations["EN"][2][ugettext('Educación en valores')][2][ugettext('Respeto y tolerancia')][ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y ") + otherStudents].append(ugettext('La suma de sus elecciones negativas o su expansividad negativa (EN) es alta') + ". ")
                    recommendations["EN"][2][ugettext('Educación en valores')][2][ugettext('Respeto y tolerancia')][ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y ") + otherStudents].append(reasons)
                    recommendations["EN"][2][ugettext('Educación en valores')][2][ugettext('Respeto y tolerancia')][ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y ") + otherStudents].append(ugettext('Si se dan las circunstancias de diversidad funcional o singularidad física o psíquica, identidad de género, diferencias socioeconómicas, etc. en él o en su entorno.'))

        otherStudents = ''
        reasons = ''
        if inValue[user][list(inValue[user])[0]] == ugettext("Alto") and imnValue[user][list(imnValue[user])[0]] == ugettext("Alto"):
            for r in matrix[4]:
                if user in matrix[4][r]:
                    o = AlumnoTests.objects.get(username=r)
                    if otherStudents == '':
                        otherStudents += o.get_nombre() + " " + o.get_apellidos()
                    else:
                        otherStudents += "/" + o.get_nombre() + " " + o.get_apellidos()
                    if alumnoCurrent != '':
                        if user in matrixText[4][r]:
                            if matrixText[4][r][user] != '':
                                reasons += o.get_nombre() + " " + o.get_apellidos() + ugettext(' piensa que lo/la rechaza por el motivo "') + matrixText[4][r][user] + '". '
                            else:
                                reasons += o.get_nombre() + " " + o.get_apellidos() + ugettext(' piensa que lo/la rechaza') + '. '
            if otherStudents != '':

                if ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y ") + otherStudents not in recommendations["IN"][1][ugettext('Educación emocional')][3][ugettext('Habilidades sociales')]:
                    recommendations["IN"][1][ugettext('Educación emocional')][3][ugettext('Habilidades sociales')][ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y ") + otherStudents] = []
                    recommendations["IN"][1][ugettext('Educación emocional')][3][ugettext('Habilidades sociales')][ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y ") + otherStudents].append(URL + etapa +"/" + Link.objects.get(name="Educación emocional").url + "/" + etapa.split('_')[1] + "_" + Link.objects.get(name="Habilidades sociales").url + '.php')
                recommendations["IN"][1][ugettext('Educación emocional')][3][ugettext('Habilidades sociales')][ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y ") + otherStudents].append(ugettext('El número de compañeros que se creen rechazados por él/ella o su impresión negativa (IN) es alta y el nivel medio de impresión que tiene el grupo de ser rechazado por él/ella (IMN) es alto') + ". ")
                recommendations["IN"][1][ugettext('Educación emocional')][3][ugettext('Habilidades sociales')][ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y ") + otherStudents].append(reasons)

        if user in osValue:
            if len(osValue[user]) > 0:
                for r in osValue[user]:
                    o = AlumnoTests.objects.get(username=r)
                    if ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y ") + o.get_nombre() + " " + o.get_apellidos() not in recommendations["OS"][1][ugettext('Educación emocional')][4][ugettext('Empatía')]:
                        recommendations["OS"][1][ugettext('Educación emocional')][4][ugettext('Empatía')][ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y ") + o.get_nombre() + " " + o.get_apellidos()] = []
                        recommendations["OS"][1][ugettext('Educación emocional')][4][ugettext('Empatía')][ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y ") + o.get_nombre() + " " + o.get_apellidos()].append(URL + etapa +"/" + Link.objects.get(name="Educación emocional").url + "/" + etapa.split('_')[1] + "_" + Link.objects.get(name="Empatía").url + '.php')
                    recommendations["OS"][1][ugettext('Educación emocional')][4][ugettext('Empatía')][ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y ") + o.get_nombre() + " " + o.get_apellidos()].append(ugettext('Tienen oposición de sentimientos (OS) de tal forma que un alumno o alumna escoge a otro que lo rechaza.') + ". ")
                    recommendations["OS"][1][ugettext('Educación emocional')][4][ugettext('Empatía')][ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y ") + o.get_nombre() + " " + o.get_apellidos()].append(osValue[user][r])

                    if ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y ") + o.get_nombre() + " " + o.get_apellidos() not in recommendations["OS"][1][ugettext('Educación emocional')][3][ugettext('Habilidades sociales')]:
                        recommendations["OS"][1][ugettext('Educación emocional')][3][ugettext('Habilidades sociales')][ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y ") + o.get_nombre() + " " + o.get_apellidos()] = []
                        recommendations["OS"][1][ugettext('Educación emocional')][3][ugettext('Habilidades sociales')][ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y ") + o.get_nombre() + " " + o.get_apellidos()].append(URL + etapa +"/" + Link.objects.get(name="Educación emocional").url + "/" + etapa.split('_')[1] + "_" + Link.objects.get(name="Habilidades sociales").url + '.php')
                    recommendations["OS"][1][ugettext('Educación emocional')][3][ugettext('Habilidades sociales')][ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y ") + o.get_nombre() + " " + o.get_apellidos()].append(ugettext('Tienen oposición de sentimientos (OS) de tal forma que un alumno o alumna escoge a otro que lo rechaza.') + ". ")
                    recommendations["OS"][1][ugettext('Educación emocional')][3][ugettext('Habilidades sociales')][ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y ") + o.get_nombre() + " " + o.get_apellidos()].append(osValue[user][r])

        if user in oipValue:
            otherStudents = ''
            reasons = ''
            if len(oipValue[user]) > 0:
                for r in oipValue[user]:
                    o = AlumnoTests.objects.get(username=r)
                    if otherStudents == '':
                        otherStudents += o.get_nombre() + " " + o.get_apellidos()
                    else:
                        otherStudents += "/" + o.get_nombre() + " " + o.get_apellidos()
                    if alumnoCurrent != '':
                        if user in matrixText[2][r]:
                            if matrixText[2][r][user] != '':
                                reasons += o.get_nombre() + " " + o.get_apellidos() + ugettext(' lo/la rechaza por el motivo "') + matrixText[2][r][user]
                            else:
                                reasons += o.get_nombre() + " " + o.get_apellidos() + ugettext(' lo/la rechaza')
                if otherStudents != '':
                    if ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y ") + otherStudents not in recommendations["OIP"][1][ugettext('Educación emocional')][3][ugettext('Habilidades sociales')]:
                        recommendations["OIP"][1][ugettext('Educación emocional')][3][ugettext('Habilidades sociales')][ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y ") + otherStudents] = []
                        recommendations["OIP"][1][ugettext('Educación emocional')][3][ugettext('Habilidades sociales')][ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y ") + otherStudents].append(URL + etapa +"/" + Link.objects.get(name="Educación emocional").url + "/" + etapa.split('_')[1] + "_" + Link.objects.get(name="Habilidades sociales").url + '.php')
                    recommendations["OIP"][1][ugettext('Educación emocional')][3][ugettext('Habilidades sociales')][ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y ") + otherStudents].append(ugettext('Contradicción entre la expectativa de ser elegido por determinados compañeros o compañeras cuando en realidad han sido rechazados por ellos'))
                    recommendations["OIP"][1][ugettext('Educación emocional')][3][ugettext('Habilidades sociales')][ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y ") + otherStudents].append(reasons + ugettext(" cuando pensaba ser elegido/a."))

        if user in rnValue:
            if rnValue[user][list(rnValue[user])[0]] == "Mayor":
                others = ''
                reasons = ''
                for r in matrix[2][user]:
                    if "#0da863" in matrix[2][user][r]:
                        o = AlumnoTests.objects.get(username=r)
                        if others == '' and (str(r) + str(user)) not in othersDone:
                            others += o.get_nombre() + " " + o.get_apellidos()
                            othersDone[str(user) + str(r)] = True
                        elif (str(r) + str(user)) not in othersDone:
                            others += "/" + o.get_nombre() + " " + o.get_apellidos()
                        if alumnoCurrent != '':
                            if r in matrixText[2][user] and user in matrixText[2][r]:
                                if matrixText[2][user][r] != '' and matrixText[2][r][user] != '':
                                    reasons += ugettext('Rechaza a ') + o.get_nombre() + " " + o.get_apellidos() + ugettext(' por el motivo "') + matrixText[2][user][r] + ugettext('" y ') + o.get_nombre() + " " + o.get_apellidos() + ugettext(' lo/la rechaza por el motivo "') + matrixText[2][r][user] + '". '
                                elif matrixText[2][user][r] != '':
                                    reasons += ugettext('Rechaza a ') + o.get_nombre() + " " + o.get_apellidos() + ugettext(' por el motivo "') + matrixText[2][user][r] + ugettext('" y ') + o.get_nombre() + " " + o.get_apellidos() + ugettext(' lo/la rechaza') + '. '
                                elif matrixText[2][r][user] != '':
                                    reasons += ugettext('Rechaza a ') + o.get_nombre() + " " + o.get_apellidos() + ugettext(' y ') + o.get_nombre() + " " + o.get_apellidos() + ugettext(' lo/la rechaza por el motivo "') + matrixText[2][r][user] + '". '
                                else:
                                    reasons += ugettext('Rechaza a ') + o.get_nombre() + " " + o.get_apellidos() + ugettext(' y ') + o.get_nombre() + " " + o.get_apellidos() + ugettext(' lo/la rechaza') + '. '
                if others != '':
                    if ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y ") + others not in recommendations["RN"][1][ugettext('Educación emocional')][5][ugettext('Resolución de conflictos')]:
                        recommendations["RN"][1][ugettext('Educación emocional')][5][ugettext('Resolución de conflictos')][ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y ") + others] = []
                        recommendations["RN"][1][ugettext('Educación emocional')][5][ugettext('Resolución de conflictos')][ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y ") + others].append(URL + etapa +"/" + Link.objects.get(name="Educación emocional").url + "/" + etapa.split('_')[1] + "_" + Link.objects.get(name="Resolución de conflictos").url + '.php')
                    recommendations["RN"][1][ugettext('Educación emocional')][5][ugettext('Resolución de conflictos')][ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y ") + others].append(ugettext('Existe enemistad o rechazos recíprocos (RN) entre ellos') + ". ")
                    recommendations["RN"][1][ugettext('Educación emocional')][5][ugettext('Resolución de conflictos')][ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y ") + others].append(reasons)

                    if ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y ") + others not in recommendations["RN"][2][ugettext('Educación en valores')][2][ugettext('Respeto y tolerancia')]:
                        recommendations["RN"][2][ugettext('Educación en valores')][2][ugettext('Respeto y tolerancia')][ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y ") + others] = []
                        recommendations["RN"][2][ugettext('Educación en valores')][2][ugettext('Respeto y tolerancia')][ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y ") + others].append(URL + etapa +"/" + Link.objects.get(name="Educación en valores").url + "/" + etapa.split('_')[1] + "_" + Link.objects.get(name="Respeto y tolerancia").url + '.php')
                    recommendations["RN"][2][ugettext('Educación en valores')][2][ugettext('Respeto y tolerancia')][ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y ") + others].append(ugettext('Cuando existan enemistad o rechazos recíprocos (RN) entre ellos y cuando se den las circunstancias de diversidad funcional o singularidad física o psíquica, identidad de género, diferencias socioeconómicas, etc.') + ". ")
                    recommendations["RN"][2][ugettext('Educación en valores')][2][ugettext('Respeto y tolerancia')][ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y ") + others].append(reasons)


        otherStudents = ''
        reasons = ''
        if snValue[user][list(snValue[user])[0]] == ugettext("Alto") and nnValue[user][list(nnValue[user])[0]] == ugettext("Alto"):
            for r in matrix[2][user]:
                o = AlumnoTests.objects.get(username=r)
                if otherStudents == '':
                    otherStudents += o.get_nombre() + " " + o.get_apellidos()
                else:
                    otherStudents += "/" + o.get_nombre() + " " + o.get_apellidos()
                if alumnoCurrent != '':
                    if r in matrixText[2][user]:
                        if matrixText[2][user][r] != '':
                            reasons += ugettext('Rechaza a ') + o.get_nombre() + " " + o.get_apellidos() + ugettext(' por el motivo "') + matrixText[2][user][r] + '". '
                        else:
                            reasons += ugettext('Rechaza a ') + o.get_nombre() + " " + o.get_apellidos() + '. '
            if otherStudents != '':
                if ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y ") + otherStudents not in recommendations["SN"][2][ugettext('Educación en valores')][1][ugettext('Interculturalidad')]:
                    recommendations["SN"][2][ugettext('Educación en valores')][1][ugettext('Interculturalidad')][ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y ") + otherStudents] = []
                    recommendations["SN"][2][ugettext('Educación en valores')][1][ugettext('Interculturalidad')][ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y ") + otherStudents].append(URL + etapa +"/" + Link.objects.get(name="Educación en valores").url + "/" + etapa.split('_')[1] + "_" + Link.objects.get(name="Interculturalidad").url + '.php')
                recommendations["SN"][2][ugettext('Educación en valores')][1][ugettext('Interculturalidad')][ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y ") + otherStudents].append(ugettext('Su estatus de eleccions negativas (SN) y su nivel medio de rechazo (NN) son altos') + ". ")
                recommendations["SN"][2][ugettext('Educación en valores')][1][ugettext('Interculturalidad')][ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y ") + otherStudents].append(reasons)
                recommendations["SN"][2][ugettext('Educación en valores')][1][ugettext('Interculturalidad')][ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y ") + otherStudents].append(ugettext('Cuando se dé la circunstancia de la multiculturalidad (raza, etnia, religión, etc.).'))

                if ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y ") + otherStudents not in recommendations["SN"][2][ugettext('Educación en valores')][2][ugettext('Respeto y tolerancia')]:
                    recommendations["SN"][2][ugettext('Educación en valores')][2][ugettext('Respeto y tolerancia')][ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y ") + otherStudents] = []
                    recommendations["SN"][2][ugettext('Educación en valores')][2][ugettext('Respeto y tolerancia')][ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y ") + otherStudents].append(URL + etapa +"/" + Link.objects.get(name="Educación en valores").url + "/" + etapa.split('_')[1] + "_" + Link.objects.get(name="Respeto y tolerancia").url + '.php')
                recommendations["SN"][2][ugettext('Educación en valores')][2][ugettext('Respeto y tolerancia')][ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y ") + otherStudents].append(ugettext('Su estatus de eleccions negativas (SN) y su nivel medio de rechazo (NN) son altos') + ". ")
                recommendations["SN"][2][ugettext('Educación en valores')][2][ugettext('Respeto y tolerancia')][ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y ") + otherStudents].append(reasons)
                recommendations["SN"][2][ugettext('Educación en valores')][2][ugettext('Respeto y tolerancia')][ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y ") + otherStudents].append(ugettext('Cuando se den las circunstancias de diversidad funcional o singularidad física o psíquica, identidad de género, diferencias socioeconómicas, etc.'))

                if ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y ") + otherStudents not in recommendations["SN"][2][ugettext('Educación en valores')][4][ugettext('Responsabilidad')]:
                    recommendations["SN"][2][ugettext('Educación en valores')][4][ugettext('Responsabilidad')][ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y ") + otherStudents] = []
                    recommendations["SN"][2][ugettext('Educación en valores')][4][ugettext('Responsabilidad')][ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y ") + otherStudents].append(URL + etapa +"/" + Link.objects.get(name="Educación en valores").url + "/" + etapa.split('_')[1] + "_" + Link.objects.get(name="Responsabilidad").url + '.php')
                recommendations["SN"][2][ugettext('Educación en valores')][4][ugettext('Responsabilidad')][ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y ") + otherStudents].append(ugettext('Su estatus de eleccions negativas (SN) y su nivel medio de rechazo (NN) son altos') + ". ")
                recommendations["SN"][2][ugettext('Educación en valores')][4][ugettext('Responsabilidad')][ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y ") + otherStudents].append(reasons)
                recommendations["SN"][2][ugettext('Educación en valores')][4][ugettext('Responsabilidad')][ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y ") + otherStudents].append(ugettext('En preguntas de ámbito formal en las que las justificaciones de los rechazos se basen en que determinado alumno o alumna no realiza su parte de trabajo de grupo.'))

        if user in pnValue and user in panValue:
            otherStudents = ''
            reasons = ''
            if pnValue[user][list(pnValue[user])[0]] == ugettext("Alto") and panValue[user][list(panValue[user])[0]] == ugettext("Alto"):
                for r in matrix[4][user]:
                    o = AlumnoTests.objects.get(username=r)
                    if otherStudents == '':
                        otherStudents += o.get_nombre() + " " + o.get_apellidos()
                    else:
                        otherStudents += "/" + o.get_nombre() + " " + o.get_apellidos()
                    if alumnoCurrent != '':
                        if r in matrixText[4][user]:
                            if matrixText[4][user][r] != '':
                                reasons += ugettext('Piensa que') + o.get_nombre() + " " + o.get_apellidos() + ugettext(' lo/la rechaza por el motivo "') + matrixText[4][user][r] + '". '
                            else:
                                reasons += ugettext('Piensa que') + o.get_nombre() + " " + o.get_apellidos() + ugettext(' lo/la rechaza') + '. '

                if otherStudents != '':
                    if ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y ") + otherStudents not in recommendations["PN"][2][ugettext('Educación en valores')][1][ugettext('Interculturalidad')]:
                        recommendations["PN"][2][ugettext('Educación en valores')][1][ugettext('Interculturalidad')][ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y ") + otherStudents] = []
                        recommendations["PN"][2][ugettext('Educación en valores')][1][ugettext('Interculturalidad')][ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y ") + otherStudents].append(URL + etapa +"/" + Link.objects.get(name="Educación en valores").url + "/" + etapa.split('_')[1] + "_" + Link.objects.get(name="Interculturalidad").url + '.php')
                    recommendations["PN"][2][ugettext('Educación en valores')][1][ugettext('Interculturalidad')][ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y ") + otherStudents].append(ugettext('El número de compañeros por los que se cree rechazado o percepción negativa (PN) es alta y su percepción acertada de ese número (PAN) es alta.') + ". ")
                    recommendations["PN"][2][ugettext('Educación en valores')][1][ugettext('Interculturalidad')][ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y ") + otherStudents].append(reasons)
                    recommendations["PN"][2][ugettext('Educación en valores')][1][ugettext('Interculturalidad')][ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y ") + otherStudents].append(ugettext('Cuando un alumno tenga un índice de percepción negativa alto y un índice de acierto alto y se dé la circunstancia de la multiculturalidad (raza, etnia, religión, etc.).'))

                    if ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y ") + otherStudents not in recommendations["PN"][2][ugettext('Educación en valores')][2][ugettext('Respeto y tolerancia')]:
                        recommendations["PN"][2][ugettext('Educación en valores')][2][ugettext('Respeto y tolerancia')][ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y ") + otherStudents] = []
                        recommendations["PN"][2][ugettext('Educación en valores')][2][ugettext('Respeto y tolerancia')][ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y ") + otherStudents].append(URL + etapa +"/" + Link.objects.get(name="Educación en valores").url + "/" + etapa.split('_')[1] + "_" + Link.objects.get(name="Respeto y tolerancia").url + '.php')
                    recommendations["PN"][2][ugettext('Educación en valores')][2][ugettext('Respeto y tolerancia')][ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y ") + otherStudents].append(ugettext('El número de compañeros por los que se cree rechazado o percepción negativa (PN) es alta y su percepción acertada de ese número (PAN) es alta y se dan las circunstancias de diversidad funcional o singularidad física o psíquica, identidad de género, diferencias socioeconómicas, etc.') + ". ")
                    recommendations["PN"][2][ugettext('Educación en valores')][2][ugettext('Respeto y tolerancia')][ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y ") + otherStudents].append(reasons)

                    if ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y ") + otherStudents not in recommendations["PN"][2][ugettext('Educación en valores')][4][ugettext('Responsabilidad')]:
                        recommendations["PN"][2][ugettext('Educación en valores')][4][ugettext('Responsabilidad')][ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y ") + otherStudents] = []
                        recommendations["PN"][2][ugettext('Educación en valores')][4][ugettext('Responsabilidad')][ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y ") + otherStudents].append(URL + etapa +"/" + Link.objects.get(name="Educación en valores").url + "/" + etapa.split('_')[1] + "_" + Link.objects.get(name="Responsabilidad").url + '.php')
                    recommendations["PN"][2][ugettext('Educación en valores')][4][ugettext('Responsabilidad')][ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y ") + otherStudents].append(ugettext('El número de compañeros por los que se cree rechazado o percepción negativa (PN) es alta y su percepción acertada de ese número (PAN) es alta en preguntas de ámbtio formal.') + ". ")
                    recommendations["PN"][2][ugettext('Educación en valores')][4][ugettext('Responsabilidad')][ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y ") + otherStudents].append(reasons)


        otherStudents = ''
        reasons = ''
        if ipnValue[user][list(ipnValue[user])[0]] == ugettext("Alto"):
            for r in matrix[6][user]:
                o = AlumnoTests.objects.get(username=r)
                if otherStudents == '':
                    otherStudents += o.get_nombre() + " " + o.get_apellidos()
                else:
                    otherStudents += "/" + o.get_nombre() + " " + o.get_apellidos()
                if alumnoCurrent != '':
                    if r in matrixText[6][user]:
                        if matrixText[6][user][r] != '':
                            reasons += o.get_nombre() + " " + o.get_apellidos() + ugettext(' lo/la elegió por el motivo "') + matrixText[6][user][r] + '". '
                        else:
                            reasons += o.get_nombre() + " " + o.get_apellidos() + ugettext(' lo/la elegió') + '. '

            if otherStudents != '':
                if ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y ") + otherStudents not in recommendations["IPN"][2][ugettext('Educación en valores')][2][ugettext('Respeto y tolerancia')]:
                    recommendations["IPN"][2][ugettext('Educación en valores')][2][ugettext('Respeto y tolerancia')][ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y ") + otherStudents] = []
                    recommendations["IPN"][2][ugettext('Educación en valores')][2][ugettext('Respeto y tolerancia')][ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y ") + otherStudents].append(URL + etapa +"/" + Link.objects.get(name="Educación en valores").url + "/" + etapa.split('_')[1] + "_" + Link.objects.get(name="Respeto y tolerancia").url + '.php')
                recommendations["IPN"][2][ugettext('Educación en valores')][2][ugettext('Respeto y tolerancia')][ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y ") + otherStudents].append(ugettext('La cantidad de veces que es nombrado/a por sus compañeros en las categorías de carácter negativo o su índice de preferencia social negativa (IPN) es alto') + ". ")
                recommendations["IPN"][2][ugettext('Educación en valores')][2][ugettext('Respeto y tolerancia')][ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y ") + otherStudents].append(reasons)
                recommendations["IPN"][2][ugettext('Educación en valores')][2][ugettext('Respeto y tolerancia')][ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y ") + otherStudents].append(ugettext('Cuando el índice afecta al atributo de "no respeta" o similar.'))

                if ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y ") + otherStudents not in recommendations["IPN"][2][ugettext('Educación en valores')][4][ugettext('Responsabilidad')]:
                    recommendations["IPN"][2][ugettext('Educación en valores')][4][ugettext('Responsabilidad')][ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y ") + otherStudents] = []
                    recommendations["IPN"][2][ugettext('Educación en valores')][4][ugettext('Responsabilidad')][ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y ") + otherStudents].append(URL + etapa +"/" + Link.objects.get(name="Educación en valores").url + "/" + etapa.split('_')[1] + "_" + Link.objects.get(name="Responsabilidad").url + '.php')
                recommendations["IPN"][2][ugettext('Educación en valores')][4][ugettext('Responsabilidad')][ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y ") + otherStudents].append(ugettext('La cantidad de veces que es nombrado/a por sus compañeros en las categorías de carácter negativo o su índice de preferencia social negativa (IPN) es alto') + ". ")
                recommendations["IPN"][2][ugettext('Educación en valores')][4][ugettext('Responsabilidad')][ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y ") + otherStudents].append(ugettext('Cuando el índice afecta al atributo de "no trabaja" o "no colabora" o similar.'))
                recommendations["IPN"][2][ugettext('Educación en valores')][4][ugettext('Responsabilidad')][ugettext("Entre ") + studentName.get_nombre() + " "  + studentName.get_apellidos() + ugettext(" y ") + otherStudents].append(reasons)

    return {'ic': icValue, 'id': idValue,
            'iap': iapValue, 'ian': ianValue, 'recomendaciones': recommendations, 'sp': spValue, 'sn': snValue, 'ep': epValue, 'en': enValue, 'pp': ppValue, 'pap': papValue, 'pn': pnValue, 'pan': panValue,
            'ip': ipValue, 'in': inValue, 'ipp': ippValue, 'ipn': ipnValue, 'imp': impValue, 'imn': imnValue}

@login_required
def show_results_complete(request, test, year):
    teacherProfile = UserProfile.objects.get(user__username=str(request.user))
    pdf = 0
    if 'Pdf' in request.path:
        pdf = 1
    test = Test.objects.get(id=test)
    preguntas = Preguntas_test.objects.filter(test=test)
    alumnos = AlumnoTests.objects.filter(idTest=test)
    respuestasNum = {}
    matrix = {}
    for num, pregunta in enumerate(preguntas):
        aux = {}
        question = {}
        respuestas = {}
        for respuesta in Respuesta.objects.filter(pregunta=pregunta):
            student = AlumnoTests.objects.get(idAl=respuesta.alumno.id, idTest=test)
            resp = {}
            j = json.loads(respuesta.respuesta)
            answers = {}
            for element in j:
                if 'text' not in element:
                    resp[j.get(element)] = {str('#ffffff'): str((MIDDLE_POINT - int(element)) + MIDDLE_POINT)}
                    answers[j.get(element)] = (MIDDLE_POINT - int(element)) + MIDDLE_POINT
            for e,a in enumerate(alumnos):
                if str(a.username) == str(student.username) or str(a.username) not in resp:
                    resp[str(a.username)] = {str('#ffffff'): str('')}
                    answers[a.username] = ''
            aux[respuesta.alumno] = resp
            question[student.username] = answers
        matrix[num+1] = question
        respuestas[pregunta.pregunta.tipo_pregunta.tipo + ": " + ugettext(pregunta.pregunta.pregunta)] = aux
        if pregunta.pregunta.tipo_pregunta.tipo == "PGP":
            respuestasNum[1] = respuestas
        elif pregunta.pregunta.tipo_pregunta.tipo == "PGN":
            respuestasNum[2] = respuestas
        elif pregunta.pregunta.tipo_pregunta.tipo == "PPP":
            respuestasNum[3] = respuestas
        elif pregunta.pregunta.tipo_pregunta.tipo == "PPN":
            respuestasNum[4] = respuestas
        elif pregunta.pregunta.tipo_pregunta.tipo == "AAP":
            respuestasNum[5] = respuestas
        elif pregunta.pregunta.tipo_pregunta.tipo == "AAN":
            respuestasNum[6] = respuestas
    mutual = 0
    os = 0
    reject = 0
    believe = 0
    believeNo = 0
    oip = 0
    oin = 0
    sp = {}
    spval = {}
    np = {}
    sn = {}
    snval = {}
    nn = {}
    ip = {}
    ipval = {}
    imp = {}
    iN = {}
    inval = {}
    imn = {}
    ipp = {}
    ipval5 = {}
    ipn = {}
    inval6 = {}
    matrix12 = {}
    matrix34 = {}
    for m in matrix:
        for answer in matrix[m]:
            answerId = AlumnoTests.objects.get(username=answer)
            if str(answer) not in matrix12:
                matrix12[str(answer)] = {}
            if 'EP' not in matrix12[str(answer)]:
                matrix12[str(answer)]['EP'] = 0
            if 'EN' not in matrix12[str(answer)]:
                matrix12[str(answer)]['EN'] = 0
            if 'RP' not in matrix12[str(answer)]:
                matrix12[str(answer)]['RP'] = 0
            if 'RN' not in matrix12[str(answer)]:
                matrix12[str(answer)]['RN'] = 0
            if str(answer) not in matrix34:
                matrix34[str(answer)] = {}
            if 'PP' not in matrix34[str(answer)]:
                matrix34[str(answer)]['PP'] = 0
            if 'PAP' not in matrix34[str(answer)]:
                matrix34[str(answer)]['PAP'] = 0
            if 'PN' not in matrix34[str(answer)]:
                matrix34[str(answer)]['PN'] = 0
            if 'PAN' not in matrix34[str(answer)]:
                matrix34[str(answer)]['PAN'] = 0
            for student in matrix[m][answer]:
                if student not in sp:
                    sp[student] = 0
                if student not in spval:
                    spval[student] = 0
                if student not in sn:
                    sn[student] = 0
                if student not in snval:
                    snval[student] = 0
                if student not in ip:
                    ip[student] = 0
                if student not in ipval:
                    ipval[student] = 0
                if student not in iN:
                    iN[student] = 0
                if student not in inval:
                    inval[student] = 0
                if student not in ipp:
                    ipp[student] = 0
                if student not in ipn:
                    ipn[student] = 0
                if student not in ipval5:
                    ipval5[student] = 0
                if student not in inval6:
                    inval6[student] = 0
                if str(matrix[m][answer][student]) != '':
                    if m == 1:
                        matrix12[str(answer)]['EP'] += 1
                        sp[student] += 1
                        spval[student] += int(matrix[m][answer][student])
                        if student in matrix[m]:
                            if str(matrix[m][student][answer]) != '':
                                mutual += 1
                                matrix12[str(answer)]['RP'] += 1
                                studentId = AlumnoTests.objects.get(username=student)

                                if '#ffffff' in respuestasNum[m][list(respuestasNum[m])[0]][answerId.idAl][str(student)]:
                                    respuestasNum[m][list(respuestasNum[m])[0]][answerId.idAl][str(student)][str('#d6c22b')] = respuestasNum[m][list(respuestasNum[m])[0]][answerId.idAl][str(student)]['#ffffff']
                                    del respuestasNum[m][list(respuestasNum[m])[0]][answerId.idAl][str(student)]['#ffffff']
                                if '#ffffff' in respuestasNum[m][list(respuestasNum[m])[0]][studentId.idAl][str(answer)]:
                                    respuestasNum[m][list(respuestasNum[m])[0]][studentId.idAl][str(answer)][str('#d6c22b')] = respuestasNum[m][list(respuestasNum[m])[0]][studentId.idAl][str(answer)]['#ffffff']
                                    del respuestasNum[m][list(respuestasNum[m])[0]][studentId.idAl][str(answer)]['#ffffff']
                            if str(matrix[m + 1][student][answer]) != '':
                                os += 1
                                studentId = AlumnoTests.objects.get(username=student)
                                if '#ffffff' in respuestasNum[m][list(respuestasNum[m])[0]][answerId.idAl][str(student)]:
                                    respuestasNum[m][list(respuestasNum[m])[0]][answerId.idAl][str(student)][str('#e05ab8')] = respuestasNum[m][list(respuestasNum[m])[0]][answerId.idAl][str(student)]['#ffffff']
                                    del respuestasNum[m][list(respuestasNum[m])[0]][answerId.idAl][str(student)]['#ffffff']
                                if '#ffffff' in respuestasNum[m+1][list(respuestasNum[m+1])[0]][studentId.idAl][str(answer)]:
                                    respuestasNum[m+1][list(respuestasNum[m+1])[0]][studentId.idAl][str(answer)][str('#e05ab8')] = respuestasNum[m+1][list(respuestasNum[m+1])[0]][studentId.idAl][str(answer)]['#ffffff']
                                    del respuestasNum[m+1][list(respuestasNum[m+1])[0]][studentId.idAl][str(answer)]['#ffffff']
                    elif m == 2:
                        matrix12[str(answer)]['EN'] += 1
                        sn[student] += 1
                        snval[student] += int(matrix[m][answer][student])
                        if student in matrix[m]:
                            if str(matrix[m][student][answer]) != '':
                                reject += 1
                                matrix12[str(answer)]['RN'] += 1
                                studentId = AlumnoTests.objects.get(username=student)

                                if '#ffffff' in respuestasNum[m][list(respuestasNum[m])[0]][answerId.idAl][str(student)]:
                                    respuestasNum[m][list(respuestasNum[m])[0]][answerId.idAl][str(student)][str('#0da863')] = respuestasNum[m][list(respuestasNum[m])[0]][answerId.idAl][str(student)]['#ffffff']
                                    del respuestasNum[m][list(respuestasNum[m])[0]][answerId.idAl][str(student)]['#ffffff']
                                if '#ffffff' in respuestasNum[m][list(respuestasNum[m])[0]][studentId.idAl][str(answer)]:
                                    respuestasNum[m][list(respuestasNum[m])[0]][studentId.idAl][str(answer)][str('#0da863')] = respuestasNum[m][list(respuestasNum[m])[0]][studentId.idAl][str(answer)]['#ffffff']
                                    del respuestasNum[m][list(respuestasNum[m])[0]][studentId.idAl][str(answer)]['#ffffff']
                    elif m == 3:
                        matrix34[str(answer)]['PP'] += 1
                        ip[student] += 1
                        ipval[student] += int(matrix[m][answer][student])
                        if student in matrix[m]:
                            if str(matrix[m-2][student][answer]) != '':
                                matrix34[str(answer)]['PAP'] += 1
                                believe += 1
                                if '#ffffff' in respuestasNum[m][list(respuestasNum[m])[0]][answerId.idAl][str(student)]:
                                    respuestasNum[m][list(respuestasNum[m])[0]][answerId.idAl][str(student)][str('#349beb')] = respuestasNum[m][list(respuestasNum[m])[0]][answerId.idAl][str(student)]['#ffffff']
                                    del respuestasNum[m][list(respuestasNum[m])[0]][answerId.idAl][str(student)]['#ffffff']
                            elif str(matrix[m-1][student][answer]) != '':
                                oip += 1
                                if '#ffffff' in respuestasNum[m][list(respuestasNum[m])[0]][answerId.idAl][str(student)]:
                                    respuestasNum[m][list(respuestasNum[m])[0]][answerId.idAl][str(student)][str('#ed3e46')] = respuestasNum[m][list(respuestasNum[m])[0]][answerId.idAl][str(student)]['#ffffff']
                                    del respuestasNum[m][list(respuestasNum[m])[0]][answerId.idAl][str(student)]['#ffffff']
                    elif m == 4:
                        matrix34[str(answer)]['PN'] += 1
                        iN[student] += 1
                        inval[student] += int(matrix[m][answer][student])
                        if student in matrix[m]:
                            if str(matrix[m-2][student][answer]) != '':
                                matrix34[str(answer)]['PAN'] += 1
                                believeNo += 1
                                if '#ffffff' in respuestasNum[m][list(respuestasNum[m])[0]][answerId.idAl][str(student)]:
                                    respuestasNum[m][list(respuestasNum[m])[0]][answerId.idAl][str(student)][str('#eb8034')] = respuestasNum[m][list(respuestasNum[m])[0]][answerId.idAl][str(student)]['#ffffff']
                                    del respuestasNum[m][list(respuestasNum[m])[0]][answerId.idAl][str(student)]['#ffffff']
                            elif str(matrix[m-3][student][answer]) != '':
                                oin += 1
                                if '#ffffff' in respuestasNum[m][list(respuestasNum[m])[0]][answerId.idAl][str(student)]:
                                    respuestasNum[m][list(respuestasNum[m])[0]][answerId.idAl][str(student)][str('#9646e0')] = respuestasNum[m][list(respuestasNum[m])[0]][answerId.idAl][str(student)]['#ffffff']
                                    del respuestasNum[m][list(respuestasNum[m])[0]][answerId.idAl][str(student)]['#ffffff']
                    elif m == 5:
                        ipval5[student] += int(matrix[m][answer][student])
                    elif m == 6:
                        inval6[student] += int(matrix[m][answer][student])
    n = len(sp)
    data1 = {}
    data1[1] = {'d': float(sum(sp.values())) / n}
    data1[2] = {'p': float(data1[1]['d']) / (n-1)}
    data1[3] = {'qq': 1 - data1[2]['p']}
    data1[4] = {'M': data1[2]['p'] * (n-1)}
    data1[5] = {'ss': math.sqrt((n-1)*data1[2]['p']*data1[3]['qq'])}
    if data1[5]['ss'] != 0:
        data1[6] = {'a': (data1[3]['qq']-data1[2]['p'])/data1[5]['ss']}
    else:
        data1[6] = {'a': 0}
    data1[7] = {'Xsup': data1[4]['M'] + get_t(data1[6]['a'], False)*data1[5]['ss']}
    data1[8] = {'Xinf': data1[4]['M'] + get_t(data1[6]['a'], True)*data1[5]['ss']}


    data2 = {}
    data2[1] = {'d': float(sum(sn.values())) / n}
    data2[2] = {'p': float(data2[1]['d']) / (n-1)}
    data2[3] = {'qq': 1 - data2[2]['p']}
    data2[4] = {'M': data2[2]['p'] * (n-1)}
    data2[5] = {'ss': math.sqrt((n-1)*data2[2]['p']*data2[3]['qq'])}
    if data2[5]['ss'] != 0:
        data2[6] = {'a': (data2[3]['qq']-data2[2]['p'])/data2[5]['ss']}
    else:
        data2[6] = {'a': 0}
    data2[7] = {'Xsup': data2[4]['M'] + get_t(data2[6]['a'], False)*data2[5]['ss']}
    data2[8] = {'Xinf': data2[4]['M'] + get_t(data2[6]['a'], True)*data2[5]['ss']}

    data3 = {}
    data3[1] = {'d': float(sum(ip.values())) / n}
    data3[2] = {'p': float(data3[1]['d']) / (n-1)}
    data3[3] = {'qq': 1 - data3[2]['p']}
    data3[4] = {'M': data3[2]['p'] * (n-1)}
    data3[5] = {'ss': math.sqrt((n-1)*data3[2]['p']*data3[3]['qq'])}
    if data3[5]['ss'] != 0:
        data3[6] = {'a': (data3[3]['qq']-data3[2]['p'])/data3[5]['ss']}
    else:
        data3[6] = {'a': 0}
    data3[7] = {'Xsup': data3[4]['M'] + get_t(data3[6]['a'], False)*data3[5]['ss']}
    data3[8] = {'Xinf': data3[4]['M'] + get_t(data3[6]['a'], True)*data3[5]['ss']}

    data4 = {}
    data4[1] = {'d': float(sum(iN.values())) / n}
    data4[2] = {'p': float(data4[1]['d']) / (n-1)}
    data4[3] = {'qq': 1 - data4[2]['p']}
    data4[4] = {'M': data4[2]['p'] * (n-1)}
    data4[5] = {'ss': math.sqrt((n-1)*data4[2]['p']*data4[3]['qq'])}
    if data4[5]['ss'] != 0:
        data4[6] = {'a': (data4[3]['qq']-data4[2]['p'])/data4[5]['ss']}
    else:
        data4[6] = {'a': 0}
    data4[7] = {'Xsup': data4[4]['M'] + get_t(data4[6]['a'], False)*data4[5]['ss']}
    data4[8] = {'Xinf': data4[4]['M'] + get_t(data4[6]['a'], True)*data4[5]['ss']}

    titlematrix12 = {1: "EP", 2: "RP", 3: "EN", 4: "RN"}
    titlematrix34 = {1: "PP", 2: "PAP", 3: "PN", 4: "PAN"}

    for s in spval:
        np[s] = int((float(spval[s]) / ((n - 1) * 5)) * 100)
        nn[s] = int((float(snval[s]) / ((n - 1) * 5)) * 100)
        imp[s] = int((float(ipval[s]) / ((n - 1) * 5)) * 100)
        imn[s] = int((float(inval[s]) / ((n - 1) * 5)) * 100)
        ipp[s] = int((float(ipval5[s]) / ((n - 1) * 5)) * 100)
        ipn[s] = int((float(inval6[s]) / ((n - 1) * 5)) * 100)

    matrix12aux = copy.deepcopy(matrix12)
    matrix34aux = copy.deepcopy(matrix34)
    ic, id, iap, ian = 0, 0, 0, 0
    for m in matrix12:
        for e in matrix12[m]:
            if e == "EP" or e == "EN":
                matrix12[m][e] = int((float(matrix12[m][e]) / MAX_POINTS) * 100)
            elif e == "RP":
                ic += matrix12[m][e]
            elif e == "RN":
                id += matrix12[m][e]
    for m in matrix34:
        for e in matrix34[m]:
            if e == "PAP":
                if matrix34[m]['PP'] != 0:
                    matrix34[m][e] = int((float(matrix34[m][e]) / matrix34[m]['PP']) * 100)
                else:
                    matrix34[m][e] = 0
            elif e == "PAN":
                if matrix34[m]['PN'] != 0:
                    matrix34[m][e] = int((float(matrix34[m][e]) / matrix34[m]['PN']) * 100)
                else:
                    matrix34[m][e] = 0
    for m in matrix34:
        for e in matrix34[m]:
            if e == "PP" or e == "PN":
                matrix34[m][e] = int((float(matrix34[m][e]) / MAX_POINTS) * 100)

    ic = int((float(ic) / ((n -1)*MAX_POINTS)) *100)
    id = int((float(id) / ((n -1)*MAX_POINTS)) *100)
    iap = int((float(sum(sp.values())) / (MAX_POINTS * n)) * 100)
    ian = int((float(sum(sn.values())) / (MAX_POINTS * n)) * 100)

    if ic >= 75:
        icValue = "Alto"
    elif 45 <= ic <= 74:
        icValue = "Medio"
    elif 25 <= ic <= 44:
        icValue = "Bajo"
    else:
        icValue = "Muy bajo"

    if id >= 75:
        idValue = "Muy alto"
    elif 45 <= id <= 74:
        idValue = "Alto"
    elif 25 <= id <= 44:
        idValue = "Medio"
    else:
        idValue = "Bajo"

    if iap >= 75:
        iapValue = "Alto"
    elif 45 <= iap <= 74:
        iapValue = "Medio"
    elif 25 <= iap <= 44:
        iapValue = "Bajo"
    else:
        iapValue = "Muy bajo"

    if ian >= 75:
        ianValue = "Muy alto"
    elif 45 <= ian <= 74:
        ianValue = "Alto"
    elif 25 <= ian <= 44:
        ianValue = "Medio"
    else:
        ianValue = "Bajo"

    alumnosInitials = {}
    aux = {}
    for al in alumnos:
        if " " not in al.get_apellidos().strip():
            if al.get_nombre()[0] + al.get_apellidos()[0] not in aux:
                alumnosInitials[al.get_nombre()[0] + al.get_apellidos()[0]] = al
                aux[al.get_nombre()[0] + al.get_apellidos()[0]] = 1
            else:
                aux[al.get_nombre()[0] + al.get_apellidos()[0]] += 1
                alumnosInitials[al.get_nombre()[0] + al.get_apellidos()[0] + str(aux[al.get_nombre()[0] + al.get_apellidos()[0]])] = al
        else:
            if al.get_nombre()[0] + al.get_apellidos().split(" ")[0][0] + al.get_apellidos().split(" ")[1][0] not in aux:
                alumnosInitials[al.get_nombre()[0] + al.get_apellidos().split(" ")[0][0] + al.get_apellidos().split(" ")[1][0]] =  al
                aux[al.get_nombre()[0] + al.get_apellidos().split(" ")[0][0] + al.get_apellidos().split(" ")[1][0]] = 1
            else:
                aux[al.get_nombre()[0] + al.get_apellidos().split(" ")[0][0] + al.get_apellidos().split(" ")[1][0]] += 1
                alumnosInitials[al.get_nombre()[0] + al.get_apellidos().split(" ")[0][0] + al.get_apellidos().split(" ")[1][0] + str(aux[al.get_nombre()[0] + al.get_apellidos().split(" ")[0][0] + al.get_apellidos().split(" ")[1][0]])] = al

    if pdf == 1:

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachement; filename="Informe-Completo-Cuestionario-{0}.pdf"'.format(test.nombre)

        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30,leftMargin=30, topMargin=100,bottomMargin=50)
        doc.pagesize = portrait(A4)
        elements = []

        #Configure style and word wrap
        s = getSampleStyleSheet()
        s = s['BodyText']
        s.wordWrap = 'CJK'
        s.fontName = 'Helvetica'
        s.alignment = 1
        s.fontSize = 20
        title = Paragraph(ugettext("Informe de grupo {0}".format(test.clase.nombre)), s)
        elements.append(title)
        s.fontSize = 10

        sLeft = getSampleStyleSheet()
        sLeft = sLeft['BodyText']
        sLeft.wordWrap = 'CJK'
        sLeft.fontName = 'Helvetica'
        sLeft.alignment = 0
        sLeft.fontSize = 10

        style = [
            ('LINEBELOW', (0, 0), (-1, -2), 0.25, colors.gray),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
            ('LINEABOVE', (0,0), (-1,0), 1, colors.gray)
        ]

        data = []
        aux = []

        aux.append(ugettext("Colegio"))
        aux.append(teacherProfile.colegio)
        data.append(aux)
        aux = []
        aux.append(ugettext("Curso y Grupo"))
        aux.append(test.clase.nombre)
        data.append(aux)
        aux = []
        aux.append(ugettext("Tutor responsable"))
        aux.append(teacherProfile.nombre + " " + teacherProfile.apellidos)
        data.append(aux)
        aux = []
        aux.append(ugettext("Nombre del test"))
        aux.append(test.nombre)
        data.append(aux)
        aux = []
        aux.append(ugettext("Fecha del test"))
        aux.append(test.date_created.strftime('%d/%m/%Y %H:%M'))
        data.append(aux)
        aux = []

        dataAux = []
        for r, row in enumerate(data):
            aux = []
            for c, cell in enumerate(row):
                if c == 0 and (0 <= r <= len(data) - 1):
                    sLeft.fontName = 'Helvetica-Oblique'
                else:
                    sLeft.fontName = 'Helvetica'
                sLeft.fontSize = 9
                aux.append(Paragraph(cell, sLeft))
            dataAux.append(aux)
        t=Table(dataAux, spaceAfter=50, spaceBefore=50)
        t.setStyle(TableStyle(style))

        elements.append(t)

        s.fontSize = 11
        elements.append(Paragraph(ugettext("Alumnos"), s))
        s.fontSize = 10

        style = [
            ('LINEBELOW', (0, 1), (-1, -2), 0.25, colors.gray),
            ('LINEBELOW', (0, 0), (-1, 0), 1, colors.gray),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
            ('LINEABOVE', (0,0), (-1,0), 1, colors.white)
        ]

        data = []
        aux = []
        aux.append(ugettext('Código'))
        aux.append(ugettext('Nombre'))
        aux.append(ugettext('Responde'))
        data.append(aux)
        aux = []
        for al in alumnos:
            for a in alumnosInitials:
                if alumnosInitials[a].username == al.username:
                    aux.append(a)
                    aux.append(alumnosInitials[a].get_nombre() + " " + alumnosInitials[a].get_apellidos())
                    if alumnosInitials[a].answer:
                        aux.append(ugettext('Sí'))
                    else:
                        aux.append(ugettext('No'))
                    data.append(aux)
                    aux = []

        dataAux = []
        for r, row in enumerate(data):
            aux = []
            for c, cell in enumerate(row):
                if r == 0:
                    sLeft.fontName = 'Helvetica-Bold'
                elif c == 0 and (1 <= r <= len(data) - 1):
                    sLeft.fontName = 'Helvetica-Oblique'
                else:
                    sLeft.fontName = 'Helvetica'
                sLeft.fontSize = 9
                aux.append(Paragraph(cell, sLeft))
            dataAux.append(aux)
        t=Table(dataAux, spaceAfter=50, spaceBefore=25)
        t.setStyle(TableStyle(style))

        elements.append(t)
        elements.append(PageBreak())

        s.fontSize = 11
        elements.append(Paragraph(ugettext("Preguntas"), s))
        s.fontSize = 10

        elements.append(Spacer(1, 0.1*inch))

        style = [
            ('LINEBELOW', (0, 1), (-1, -2), 0.25, colors.gray),
            ('LINEBELOW', (0, 0), (-1, 0), 1, colors.gray),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
            ('LINEABOVE', (0,0), (-1,0), 1, colors.white),
            ('LINEBEFORE', (1, 1), (-1, -1), 0.25, colors.gray)
        ]

        data = []
        aux = []
        row = 0
        col = 0
        for question in respuestasNum:
            aux.append(str(question) + '#')
            for al in alumnos:
                for a in alumnosInitials:
                    if alumnosInitials[a].username == al.username:
                        aux.append(a)
            data.append(aux)
            row += 1
            aux =[]
            for questionName in respuestasNum[question]:
                title = Paragraph(questionName, s)
                elements.append(title)
                for al in alumnos:
                    for a in alumnosInitials:
                        if alumnosInitials[a].username == al.username:
                            for studentAnswer in respuestasNum[question][questionName]:
                                if studentAnswer.id == alumnosInitials[a].idAl.id:
                                    aux.append(a)
                                    col += 1
                                    for al in alumnos:
                                        for answers in respuestasNum[question][questionName][studentAnswer]:
                                            if answers == al.username:
                                                for an in respuestasNum[question][questionName][studentAnswer][answers]:
                                                    aux.append(respuestasNum[question][questionName][studentAnswer][answers][an])
                                                    style.append(('BACKGROUND',(col,row),(col,row), colors.HexColor(an)))
                                                    col += 1
                                    data.append(aux)
                                    row += 1
                                    col = 0
                                    aux = []

            dataAux = []
            for r, row in enumerate(data):
                aux = []
                for c, cell in enumerate(row):
                    if c == 0 and (1 <= r <= len(data) - 1):
                        sLeft.fontName = 'Helvetica-Oblique'
                    elif (0 <= c <= len(row) -1) and r == 0:
                        sLeft.fontName = 'Helvetica-Bold'
                    else:
                        sLeft.fontName = 'Helvetica'
                    sLeft.fontSize = 9
                    aux.append(Paragraph(cell, sLeft))
                dataAux.append(aux)
            t=Table(dataAux, spaceAfter=50, spaceBefore=20)
            t.setStyle(TableStyle(style))

            elements.append(t)
            style = [
                ('LINEBELOW', (0, 1), (-1, -2), 0.25, colors.gray),
                ('LINEBELOW', (0, 0), (-1, 0), 1, colors.gray),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
                ('LINEABOVE', (0,0), (-1,0), 1, colors.white),
                ('LINEBEFORE', (1, 1), (-1, -1), 0.25, colors.gray)
            ]
            data = []
            aux = []
            row = 0
            col = 0

        s.fontSize = 11
        elements.append(Paragraph(ugettext("Cálculo de variables"), s))
        s.fontSize = 10
        elements.append(Paragraph(ugettext("Matriz pregunta tipo 1"), s))


        aux.append('#')
        colWidths = (10*mm,)
        for al in alumnos:
            for a in alumnosInitials:
                if alumnosInitials[a].username == al.username:
                    aux.append(a)
                    colWidths = colWidths + (None,)
        data.append(aux)
        aux =[]
        aux.append("SP")
        for a in alumnos:
            for spuser in sp:
                if spuser == a.username:
                    aux.append(str(sp[spuser]))
        data.append(aux)
        aux = []
        aux.append("SP val")
        for a in alumnos:
            for spuser in spval:
                if spuser == a.username:
                    aux.append(str(spval[spuser]))
        data.append(aux)
        aux = []
        aux.append("NP")
        for a in alumnos:
            for spuser in np:
                if spuser == a.username:
                    aux.append(str(np[spuser])+"%")
        data.append(aux)
        aux = []

        dataAux = []
        for r, row in enumerate(data):
            aux = []
            for c, cell in enumerate(row):
                if c == 0 and (1 <= r <= len(data) - 1):
                    sLeft.fontName = 'Helvetica-Oblique'
                    sLeft.textColor = 'black'
                elif (0 <= c <= len(row) -1) and r == 0:
                    sLeft.fontName = 'Helvetica-Bold'
                    sLeft.textColor = 'black'
                else:
                    sLeft.fontName = 'Helvetica'
                    if r == 1:
                        percent = int(cell)
                        if percent < data1[8]['Xinf']:
                            sLeft.textColor = 'red'
                        else:
                            sLeft.textColor = 'black'
                    elif r == 3:
                        percent = int(cell[0:-1])
                        if percent <= 25:
                            sLeft.textColor = 'red'
                        else:
                            sLeft.textColor = 'black'
                    else:
                        sLeft.textColor = 'black'
                sLeft.fontSize = 9
                aux.append(Paragraph(cell, sLeft))
            dataAux.append(aux)
        t=Table(dataAux, spaceAfter=50, spaceBefore=20, colWidths=colWidths)
        t.setStyle(TableStyle(style))

        elements.append(t)
        style = [
            ('LINEBELOW', (0, 0), (-1, -2), 0.25, colors.gray),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
        ]
        data = []
        aux = []

        for dnum in data1:
            for da in data1[dnum]:
                aux.append(da)
                aux.append(round(data1[dnum][da], 2))
                data.append(aux)
                aux = []

        dataAux = []
        for r, row in enumerate(data):
            aux = []
            for c, cell in enumerate(row):
                if c == 0 and (0 <= r <= len(data) - 1):
                    sLeft.fontName = 'Helvetica-Oblique'
                    sLeft.textColor = 'black'
                else:
                    sLeft.fontName = 'Helvetica'
                    sLeft.textColor = 'black'
                sLeft.fontSize = 9
                aux.append(Paragraph(str(cell), sLeft))
            dataAux.append(aux)
        t=Table(dataAux, spaceAfter=50, spaceBefore=20)
        t.setStyle(TableStyle(style))
        elements.append(t)

        style = [
            ('LINEABOVE', (0, 0), (1, 0), 0.25, colors.gray),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
            ('BACKGROUND',(0,0),(0,0), colors.HexColor("#d6c22b"))
        ]
        data = []
        aux = []
        aux.append(ugettext('Se eligen mutuamente'))
        aux.append(str(int(mutual/2)))
        data.append(aux)
        aux = []

        dataAux = []
        for r, row in enumerate(data):
            aux = []
            for c, cell in enumerate(row):
                sLeft.fontName = 'Helvetica'
                sLeft.fontSize = 9
                sLeft.textColor = 'black'
                aux.append(Paragraph(cell, sLeft))
            dataAux.append(aux)
        t=Table(dataAux, spaceAfter=50, spaceBefore=20)
        t.setStyle(TableStyle(style))
        elements.append(t)



        style = [
            ('LINEBELOW', (0, 1), (-1, -2), 0.25, colors.gray),
            ('LINEBELOW', (0, 0), (-1, 0), 1, colors.gray),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
            ('LINEABOVE', (0,0), (-1,0), 1, colors.white),
            ('LINEBEFORE', (1, 1), (-1, -1), 0.25, colors.gray)
        ]
        data = []
        aux = []
        s.fontSize = 10
        elements.append(Paragraph(ugettext("Matriz pregunta tipo 2"), s))


        aux.append('#')
        colWidths = (10*mm,)
        for al in alumnos:
            for a in alumnosInitials:
                if alumnosInitials[a].username == al.username:
                    aux.append(a)
                    colWidths = colWidths + (None,)
        data.append(aux)
        aux =[]
        aux.append("SN")
        for a in alumnos:
            for user in sn:
                if user == a.username:
                    aux.append(str(sn[user]))
        data.append(aux)
        aux = []
        aux.append("SN val")
        for a in alumnos:
            for user in snval:
                if user == a.username:
                    aux.append(str(snval[user]))
        data.append(aux)
        aux = []
        aux.append("NN")
        for a in alumnos:
            for user in nn:
                if user == a.username:
                    aux.append(str(nn[user])+"%")
        data.append(aux)
        aux = []

        dataAux = []
        for r, row in enumerate(data):
            aux = []
            for c, cell in enumerate(row):
                if c == 0 and (1 <= r <= len(data) - 1):
                    sLeft.fontName = 'Helvetica-Oblique'
                    sLeft.textColor = 'black'
                elif (0 <= c <= len(row) -1) and r == 0:
                    sLeft.fontName = 'Helvetica-Bold'
                    sLeft.textColor = 'black'
                else:
                    sLeft.fontName = 'Helvetica'
                    if r == 1:
                        percent = int(cell)
                        if percent >= data2[7]['Xsup']:
                            sLeft.textColor = 'red'
                        else:
                            sLeft.textColor = 'black'
                    elif r == 3:
                        percent = int(cell[0:-1])
                        if percent >= 75:
                            sLeft.textColor = 'red'
                        else:
                            sLeft.textColor = 'black'
                    else:
                        sLeft.textColor = 'black'
                sLeft.fontSize = 9
                aux.append(Paragraph(cell, sLeft))
            dataAux.append(aux)
        t=Table(dataAux, spaceAfter=50, spaceBefore=20, colWidths=colWidths)
        t.setStyle(TableStyle(style))

        elements.append(t)
        style = [
            ('LINEBELOW', (0, 0), (-1, -2), 0.25, colors.gray),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
        ]
        data = []
        aux = []

        for dnum in data2:
            for da in data2[dnum]:
                aux.append(da)
                aux.append(str(round(data2[dnum][da], 2)))
                data.append(aux)
                aux = []

        dataAux = []
        for r, row in enumerate(data):
            aux = []
            for c, cell in enumerate(row):
                if c == 0 and (0 <= r <= len(data) - 1):
                    sLeft.fontName = 'Helvetica-Oblique'
                    sLeft.textColor = 'black'
                else:
                    sLeft.fontName = 'Helvetica'
                    sLeft.textColor = 'black'
                sLeft.fontSize = 9
                aux.append(Paragraph(cell, sLeft))
            dataAux.append(aux)
        t=Table(dataAux, spaceAfter=50, spaceBefore=20)
        t.setStyle(TableStyle(style))
        elements.append(t)

        style = [
            ('LINEABOVE', (0, 0), (1, 0), 0.25, colors.gray),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
            ('BACKGROUND',(0,0),(0,0), colors.HexColor("#0da863"))
        ]
        data = []
        aux = []
        aux.append(ugettext('Se rechazan mutuamente'))
        aux.append(str(int(reject/2)))
        data.append(aux)
        aux = []

        dataAux = []
        for r, row in enumerate(data):
            aux = []
            for c, cell in enumerate(row):
                sLeft.fontName = 'Helvetica'
                sLeft.fontSize = 9
                sLeft.textColor = 'black'
                aux.append(Paragraph(cell, sLeft))
            dataAux.append(aux)
        t=Table(dataAux, spaceAfter=50, spaceBefore=20)
        t.setStyle(TableStyle(style))
        elements.append(t)



        style = [
            ('LINEBELOW', (0, 1), (-1, -2), 0.25, colors.gray),
            ('LINEBELOW', (0, 0), (-1, 0), 1, colors.gray),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
            ('LINEABOVE', (0,0), (-1,0), 1, colors.white)
        ]
        data = []
        aux = []
        s.fontSize = 10
        elements.append(Paragraph(ugettext("Matrices preguntas tipo 1 y 2"), s))

        aux.append('#')
        for t in titlematrix12:
            aux.append(titlematrix12[t])
        data.append(aux)
        aux =[]
        for al in alumnos:
            for a in alumnosInitials:
                if alumnosInitials[a].username == al.username:
                    for student in matrix12:
                        if student == alumnosInitials[a].username:
                            aux.append(a)
                            for ti in titlematrix12:
                                for value in matrix12[student]:
                                    if value == titlematrix12[ti]:
                                        if value == "EP" or value == "EN":
                                            aux.append(str(matrix12[student][value]) + "%")
                                        else:
                                            aux.append(str(matrix12[student][value]))
                            data.append(aux)
                            aux = []

        dataAux = []

        for r, row in enumerate(data):
            aux = []
            for c, cell in enumerate(row):
                if c == 0 and (1 <= r <= len(data) - 1):
                    sLeft.fontName = 'Helvetica-Oblique'
                    sLeft.textColor = 'black'
                elif (0 <= c <= len(row) -1) and r == 0:
                    sLeft.fontName = 'Helvetica-Bold'
                    sLeft.textColor = 'black'
                else:
                    sLeft.fontName = 'Helvetica'
                    if c == 1:
                        percent = int(cell[0:-1])
                        if percent <= 25:
                            sLeft.textColor = 'red'
                        else:
                            sLeft.textColor = 'black'
                    elif c == 3:
                        percent = int(cell[0:-1])
                        if percent >= 75:
                            sLeft.textColor = 'red'
                        else:
                            sLeft.textColor = 'black'
                    else:
                        sLeft.textColor = 'black'
                sLeft.fontSize = 9
                aux.append(Paragraph(cell, sLeft))
            dataAux.append(aux)
        t=Table(dataAux, spaceAfter=50, spaceBefore=20)
        t.setStyle(TableStyle(style))

        elements.append(t)

        style = [
            ('LINEABOVE', (0, 0), (1, 0), 0.25, colors.gray),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
            ('BACKGROUND',(0,0),(0,0), colors.HexColor("#e05ab8"))
        ]
        data = []
        aux = []
        aux.append('OS')
        aux.append(str(os))
        data.append(aux)
        aux = []

        dataAux = []
        for r, row in enumerate(data):
            aux = []
            for c, cell in enumerate(row):
                sLeft.fontName = 'Helvetica'
                sLeft.fontSize = 9
                aux.append(Paragraph(cell, sLeft))
            dataAux.append(aux)
        t=Table(dataAux, spaceAfter=50, spaceBefore=20)
        t.setStyle(TableStyle(style))
        elements.append(t)

        style = [
            ('LINEBELOW', (0, 1), (-1, -2), 0.25, colors.gray),
            ('LINEBELOW', (0, 0), (-1, 0), 1, colors.gray),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
            ('LINEABOVE', (0,0), (-1,0), 1, colors.white)
        ]
        data = []
        aux = []
        s.fontSize = 10
        elements.append(Paragraph(ugettext("Índices grupales"), s))

        aux.append('Ic')
        aux.append('Iap')
        data.append(aux)
        aux = []
        aux.append(str(ic) + "% - " + icValue)
        aux.append(str(iap) + "% - " + iapValue)
        data.append(aux)

        dataAux = []
        for r, row in enumerate(data):
            aux = []
            for c, cell in enumerate(row):
                if (0 <= c <= len(row) -1) and r == 0:
                    sLeft.fontName = 'Helvetica-Bold'
                    sLeft.textColor = 'black'
                else:
                    sLeft.fontName = 'Helvetica'
                    if c == 0:
                        if gettext("Bajo") in cell or gettext("Muy bajo"):
                            sLeft.textColor = 'red'
                        else:
                            sLeft.textColor = 'black'
                    else:
                        if gettext("Muy bajo") in cell:
                            sLeft.textColor = 'red'
                        else:
                            sLeft.textColor = 'black'
                sLeft.fontSize = 9
                aux.append(Paragraph(cell, sLeft))
            dataAux.append(aux)
        t=Table(dataAux, spaceBefore=20)
        t.setStyle(TableStyle(style))
        elements.append(t)

        data = []
        aux = []
        aux.append('Id')
        aux.append('Ian')
        data.append(aux)
        aux = []
        aux.append(str(id) + "% - " + idValue)
        aux.append(str(ian) + "% - " + ianValue)
        data.append(aux)

        dataAux = []
        for r, row in enumerate(data):
            aux = []
            for c, cell in enumerate(row):
                if (0 <= c <= len(row) -1) and r == 0:
                    sLeft.fontName = 'Helvetica-Bold'
                    sLeft.textColor = 'black'
                else:
                    sLeft.fontName = 'Helvetica'
                    if c == 0:
                        if gettext("Alto") in cell or gettext("Muy alto") in cell:
                            sLeft.textColor = 'red'
                        else:
                            sLeft.textColor = 'black'
                    else:
                        if gettext("Muy alto") in cell:
                            sLeft.textColor = 'red'
                        else:
                            sLeft.textColor = 'black'
                sLeft.fontSize = 9
                aux.append(Paragraph(cell, sLeft))
            dataAux.append(aux)
        t=Table(dataAux, spaceAfter=50, spaceBefore=20)
        t.setStyle(TableStyle(style))
        elements.append(t)


        style = [
            ('LINEBELOW', (0, 1), (-1, -2), 0.25, colors.gray),
            ('LINEBELOW', (0, 0), (-1, 0), 1, colors.gray),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
            ('LINEABOVE', (0,0), (-1,0), 1, colors.white),
            ('LINEBEFORE', (1, 1), (-1, -1), 0.25, colors.gray)
        ]
        data = []
        aux = []
        s.fontSize = 10
        elements.append(Paragraph(ugettext("Matriz pregunta tipo 3"), s))

        aux.append('#')
        colWidths = (9.75*mm,)
        for al in alumnos:
            for a in alumnosInitials:
                if alumnosInitials[a].username == al.username:
                    aux.append(a)
                    colWidths = colWidths + (None,)
        data.append(aux)
        aux =[]
        aux.append("IP")
        for a in alumnos:
            for user in ip:
                if user == a.username:
                    aux.append(str(ip[user]))
        data.append(aux)
        aux = []
        aux.append("IP val")
        for a in alumnos:
            for user in snval:
                if user == a.username:
                    aux.append(str(ipval[user]))
        data.append(aux)
        aux = []
        aux.append("Imp")
        for a in alumnos:
            for user in nn:
                if user == a.username:
                    aux.append(str(imp[user]) + "%")
        data.append(aux)
        aux = []

        dataAux = []
        for r, row in enumerate(data):
            aux = []
            for c, cell in enumerate(row):
                if c == 0 and (1 <= r <= len(data) - 1):
                    sLeft.fontName = 'Helvetica-Oblique'
                    sLeft.textColor = 'black'
                elif (0 <= c <= len(row) -1) and r == 0:
                    sLeft.fontName = 'Helvetica-Bold'
                    sLeft.textColor = 'black'
                else:
                    sLeft.fontName = 'Helvetica'
                    if r == 1:
                        percent = int(cell)
                        if percent < data3[8]['Xinf']:
                            sLeft.textColor = 'red'
                        else:
                            sLeft.textColor = 'black'
                    elif r == 3:
                        percent = int(cell[0:-1])
                        if percent >= 75:
                            sLeft.textColor = 'red'
                        else:
                            sLeft.textColor = 'black'
                    else:
                        sLeft.textColor = 'black'
                sLeft.fontSize = 9
                aux.append(Paragraph(cell, sLeft))
            dataAux.append(aux)
        t=Table(dataAux, spaceAfter=50, spaceBefore=20, colWidths=colWidths)
        t.setStyle(TableStyle(style))

        elements.append(t)
        style = [
            ('LINEBELOW', (0, 0), (-1, -2), 0.25, colors.gray),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
        ]
        data = []
        aux = []

        for dnum in data3:
            for da in data3[dnum]:
                aux.append(da)
                aux.append(str(round(data3[dnum][da], 2)))
                data.append(aux)
                aux = []

        dataAux = []
        for r, row in enumerate(data):
            aux = []
            for c, cell in enumerate(row):
                if c == 0 and (0 <= r <= len(data) - 1):
                    sLeft.fontName = 'Helvetica-Oblique'
                    sLeft.textColor = 'black'
                else:
                    sLeft.fontName = 'Helvetica'
                    sLeft.textColor = 'black'
                sLeft.fontSize = 9
                aux.append(Paragraph(cell, sLeft))
            dataAux.append(aux)
        t=Table(dataAux, spaceAfter=50, spaceBefore=20)
        t.setStyle(TableStyle(style))
        elements.append(t)


        style = [
            ('LINEBELOW', (0, 1), (-1, -2), 0.25, colors.gray),
            ('LINEBELOW', (0, 0), (-1, 0), 1, colors.gray),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
            ('LINEABOVE', (0,0), (-1,0), 1, colors.white),
            ('LINEBEFORE', (1, 1), (-1, -1), 0.25, colors.gray)
        ]
        data = []
        aux = []
        s.fontSize = 10
        elements.append(Paragraph(ugettext("Matriz pregunta tipo 4"), s))

        aux.append('#')
        colWidths = (9.75*mm,)
        for al in alumnos:
            for a in alumnosInitials:
                if alumnosInitials[a].username == al.username:
                    aux.append(a)
                    colWidths = colWidths + (None,)
        data.append(aux)
        aux =[]
        aux.append("IN")
        for a in alumnos:
            for user in iN:
                if user == a.username:
                    aux.append(str(iN[user]))
        data.append(aux)
        aux = []
        aux.append("IN val")
        for a in alumnos:
            for user in inval:
                if user == a.username:
                    aux.append(str(inval[user]))
        data.append(aux)
        aux = []
        aux.append("Imn")
        for a in alumnos:
            for user in imn:
                if user == a.username:
                    aux.append(str(imn[user]) + "%")
        data.append(aux)
        aux = []

        dataAux = []
        for r, row in enumerate(data):
            aux = []
            for c, cell in enumerate(row):
                if c == 0 and (1 <= r <= len(data) - 1):
                    sLeft.fontName = 'Helvetica-Oblique'
                    sLeft.textColor = 'black'
                elif (0 <= c <= len(row) -1) and r == 0:
                    sLeft.fontName = 'Helvetica-Bold'
                    sLeft.textColor = 'black'
                else:
                    sLeft.fontName = 'Helvetica'
                    if r == 1:
                        percent = int(cell)
                        if percent >= data4[7]['Xsup']:
                            sLeft.textColor = 'red'
                        else:
                            sLeft.textColor = 'black'
                    elif r == 3:
                        percent = int(cell[0:-1])
                        if percent >= 75:
                            sLeft.textColor = 'red'
                        else:
                            sLeft.textColor = 'black'
                    else:
                        sLeft.textColor = 'black'
                sLeft.fontSize = 9
                aux.append(Paragraph(cell, sLeft))
            dataAux.append(aux)
        t=Table(dataAux, spaceAfter=50, spaceBefore=20, colWidths=colWidths)
        t.setStyle(TableStyle(style))

        elements.append(t)
        style = [
            ('LINEBELOW', (0, 0), (-1, -2), 0.25, colors.gray),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
        ]
        data = []
        aux = []

        for dnum in data4:
            for da in data4[dnum]:
                aux.append(da)
                aux.append(str(round(data4[dnum][da], 2)))
                data.append(aux)
                aux = []

        dataAux = []
        for r, row in enumerate(data):
            aux = []
            for c, cell in enumerate(row):
                if c == 0 and (0 <= r <= len(data) - 1):
                    sLeft.fontName = 'Helvetica-Oblique'
                    sLeft.textColor = 'black'
                else:
                    sLeft.fontName = 'Helvetica'
                    sLeft.textColor = 'black'
                sLeft.fontSize = 9
                aux.append(Paragraph(cell, sLeft))
            dataAux.append(aux)
        t=Table(dataAux, spaceAfter=50, spaceBefore=20)
        t.setStyle(TableStyle(style))
        elements.append(t)



        style = [
            ('LINEBELOW', (0, 1), (-1, -2), 0.25, colors.gray),
            ('LINEBELOW', (0, 0), (-1, 0), 1, colors.gray),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
            ('LINEABOVE', (0,0), (-1,0), 1, colors.white)
        ]
        data = []
        aux = []

        aux.append('#')
        for t in titlematrix34:
            aux.append(titlematrix34[t])
        data.append(aux)
        aux =[]
        for al in alumnos:
            for a in alumnosInitials:
                if alumnosInitials[a].username == al.username:
                    for student in matrix34:
                        if student == alumnosInitials[a].username:
                            aux.append(a)
                            for ti in titlematrix34:
                                for value in matrix34[student]:
                                    if value == titlematrix34[ti]:
                                        if value == "PP" or value == "PN":
                                            aux.append(str(matrix34[student][value]) + "%")
                                        else:
                                            aux.append(str(matrix34[student][value]))
                            data.append(aux)
                            aux = []

        dataAux = []

        for r, row in enumerate(data):
            aux = []
            for c, cell in enumerate(row):
                if c == 0 and (1 <= r <= len(data) - 1):
                    sLeft.fontName = 'Helvetica-Oblique'
                    sLeft.textColor = 'black'
                elif (0 <= c <= len(row) -1) and r == 0:
                    sLeft.fontName = 'Helvetica-Bold'
                    sLeft.textColor = 'black'
                else:
                    sLeft.fontName = 'Helvetica'
                    if c == 1:
                        percent = int(cell[0:-1])
                        if percent <= 25:
                            sLeft.textColor = 'red'
                        else:
                            sLeft.textColor = 'black'
                    elif c == 3:
                        percent = int(cell[0:-1])
                        if percent >= 75:
                            sLeft.textColor = 'red'
                        else:
                            sLeft.textColor = 'black'
                    else:
                        sLeft.textColor = 'black'
                sLeft.fontSize = 9
                aux.append(Paragraph(cell, sLeft))
            dataAux.append(aux)
        t=Table(dataAux, spaceAfter=50, spaceBefore=20)
        t.setStyle(TableStyle(style))

        elements.append(t)

        style = [
            ('LINEABOVE', (0, 0), (1, -1), 0.25, colors.gray),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
            ('BACKGROUND',(0,0),(0,0), colors.HexColor("#349beb")),
            ('BACKGROUND',(0,1),(0,1), colors.HexColor("#ed3e46")),
            ('BACKGROUND',(0,2),(0,2), colors.HexColor("#eb8034")),
            ('BACKGROUND',(0,3),(0,3), colors.HexColor("#9646e0")) ]

        data = []
        aux = []
        aux.append(ugettext('Cree que lo eligen y acierta'))
        aux.append(str(believe))
        data.append(aux)
        aux = []
        aux.append('OIP')
        aux.append(str(oip))
        data.append(aux)
        aux = []
        aux.append(ugettext('Cree que lo rechazan y acierta'))
        aux.append(str(believeNo))
        data.append(aux)
        aux = []
        aux.append('OIN')
        aux.append(str(oin))
        data.append(aux)
        aux = []

        dataAux = []
        for r, row in enumerate(data):
            aux = []
            for c, cell in enumerate(row):
                sLeft.fontName = 'Helvetica'
                sLeft.fontSize = 9
                aux.append(Paragraph(cell, sLeft))
            dataAux.append(aux)
        t=Table(dataAux, spaceAfter=50, spaceBefore=20)
        t.setStyle(TableStyle(style))
        elements.append(t)


        style = [
            ('LINEBELOW', (0, 1), (-1, -2), 0.25, colors.gray),
            ('LINEBELOW', (0, 0), (-1, 0), 1, colors.gray),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
            ('LINEABOVE', (0,0), (-1,0), 1, colors.white),
            ('LINEBEFORE', (1, 1), (-1, -1), 0.25, colors.gray)
        ]
        data = []
        aux = []
        s.fontSize = 10
        elements.append(Paragraph(ugettext("Matriz pregunta tipo 5"), s))

        aux.append('#')
        colWidths = (10*mm,)
        for al in alumnos:
            for a in alumnosInitials:
                if alumnosInitials[a].username == al.username:
                    aux.append(a)
                    colWidths = colWidths + (None,)
        data.append(aux)
        aux =[]
        aux.append("IPP")
        for a in alumnos:
            for user in ipp:
                if user == a.username:
                    aux.append(str(ipp[user]) + "%")
        data.append(aux)

        dataAux = []
        for r, row in enumerate(data):
            aux = []
            for c, cell in enumerate(row):
                if c == 0 and (1 <= r <= len(data) - 1):
                    sLeft.fontName = 'Helvetica-Oblique'
                    sLeft.textColor = 'black'
                elif (0 <= c <= len(row) -1) and r == 0:
                    sLeft.fontName = 'Helvetica-Bold'
                    sLeft.textColor = 'black'
                else:
                    sLeft.fontName = 'Helvetica'
                    if r == 1:
                        percent = int(cell[0:-1])
                        if percent >= 75:
                            sLeft.textColor = 'red'
                        else:
                            sLeft.textColor = 'black'
                sLeft.fontSize = 9
                aux.append(Paragraph(cell, sLeft))
            dataAux.append(aux)
        t=Table(dataAux, spaceAfter=50, spaceBefore=20, colWidths=colWidths)
        t.setStyle(TableStyle(style))

        elements.append(t)


        data = []
        aux = []
        s.fontSize = 10
        elements.append(Paragraph(ugettext("Matriz pregunta tipo 6"), s))

        aux.append('#')
        colWidths = (10*mm,)
        for al in alumnos:
            for a in alumnosInitials:
                if alumnosInitials[a].username == al.username:
                    aux.append(a)
                    colWidths = colWidths + (None,)
        data.append(aux)
        aux =[]
        aux.append("IPN")
        for a in alumnos:
            for user in ipn:
                if user == a.username:
                    aux.append(str(ipn[user]) + "%")
        data.append(aux)

        dataAux = []
        for r, row in enumerate(data):
            aux = []
            for c, cell in enumerate(row):
                if c == 0 and (1 <= r <= len(data) - 1):
                    sLeft.fontName = 'Helvetica-Oblique'
                    sLeft.textColor = 'black'
                elif (0 <= c <= len(row) -1) and r == 0:
                    sLeft.fontName = 'Helvetica-Bold'
                    sLeft.textColor = 'black'
                else:
                    sLeft.fontName = 'Helvetica'
                    if r == 1:
                        percent = int(cell[0:-1])
                        if percent >= 75:
                            sLeft.textColor = 'red'
                        else:
                            sLeft.textColor = 'black'
                s.fontSize = 9
                aux.append(Paragraph(cell, sLeft))
            dataAux.append(aux)
        t=Table(dataAux, spaceAfter=50, spaceBefore=20, colWidths=colWidths)
        t.setStyle(TableStyle(style))

        elements.append(t)

        matrixaux = {}

        for ma in respuestasNum:
            matrixaux[ma] = {}
            for re in respuestasNum[ma]:
                for al in respuestasNum[ma][re]:
                    useral = AlumnoTests.objects.get(idAl=al, idTest=test)
                    matrixaux[ma][useral.username] = {}
                    for res in respuestasNum[ma][re][al]:
                        matrixaux[ma][useral.username][res] = respuestasNum[ma][re][al][res]


        proposals = get_proposals(sp, np, nn, sn, spval, snval, imp, ipval, imn, inval, iN, ip, ipp, ipval5, ipn, inval6, data1, data2, data3, data4, n, matrix12aux, matrix34aux, matrixaux, '', {}, test.clase.grupo_edad_id)


        elements.append(PageBreak())

        s.fontSize = 11
        elements.append(Paragraph(ugettext("Propuesta de intervención grupal"), s))
        s.fontSize = 10
        elements.append(Paragraph(ugettext("Áreas"), s))
        elements.append(Spacer(1, 0.1*inch))
        d = Drawing(760, 1)
        d.add(Line(0, 0, 760, 0))
        elements.append(d)
        elements.append(Spacer(1, 0.25*inch))

        listProposals = []
        for vari in proposals['recomendaciones']:
            if ((vari == "IC" or vari == "ID") and not_empty(proposals['recomendaciones'][vari])):
                listProposals.append(ListItem(Paragraph(vari + ": " + return_des(proposals['recomendaciones'][vari]),sLeft), spaceAfter=10))
                firstList = []
                for varinum in proposals['recomendaciones'][vari]:
                    for ex in proposals['recomendaciones'][vari][varinum]:
                        if (not_empty_ex(proposals['recomendaciones'][vari][varinum][ex])):
                            firstList.append(ListItem(Paragraph(ex,sLeft), spaceAfter=10))
                            secondList = []
                            for num in proposals['recomendaciones'][vari][varinum][ex]:
                                for secondArea in proposals['recomendaciones'][vari][varinum][ex][num]:
                                    if len(proposals['recomendaciones'][vari][varinum][ex][num][secondArea]):
                                        secondList.append(ListItem(Paragraph(secondArea,sLeft), spaceAfter=10))
                                        for studentProp in proposals['recomendaciones'][vari][varinum][ex][num][secondArea]:
                                            reasonsList = []
                                            for i, reasons in enumerate(proposals['recomendaciones'][vari][varinum][ex][num][secondArea][studentProp]):
                                                if i != 0 and i != 1:
                                                    reasonsList.append(ListItem(Paragraph(reasons,sLeft)))
                                            secondList.append(ListItem(ListFlowable(reasonsList, bulletType='bullet', start='diamond', leftIndent=10,
                                                                                    bulletFontSize=7, bulletOffsetY=-2), bulletColor="white", spaceAfter=15))
                            firstList.append(ListItem(ListFlowable(secondList, bulletType='bullet', start='rarrowhead', leftIndent=10,
                                                                    bulletFontSize=7, bulletOffsetY=-2), bulletColor="white", spaceAfter=15))
                listProposals.append(ListItem(ListFlowable(firstList, bulletType='bullet', start='square', leftIndent=10, bulletFontSize=5,
                                                    bulletOffsetY=-3), bulletColor="white", spaceAfter=20))
        t = ListFlowable(listProposals, bulletType='bullet', bulletOffsetY=2)


        elements.append(t)
        doc.multiBuild(elements, canvasmaker=FooterCanvas)
        pdfPrint = buffer.getvalue()
        buffer.close()
        response.write(pdfPrint)
        return response
    else:
        return render(request, 'resultados/datos.html',
                  {'test': test, 'clase': test.clase.nombre, 'preguntas': preguntas, 'alumnos': alumnos, 'spValue': data1[8]['Xinf'], 'snValue': data2[7]['Xsup'], 'ipValue': data3[8]['Xinf'], 'inValue': data4[7]['Xsup'],
                   'respuestasNum': respuestasNum, 'mutual': int(mutual/2), 'os': os, 'reject': int(reject/2), 'believe': believe, 'believeNo': believeNo, 'oip': oip, 'oin': oin,
                   'sp': sp, 'spval': spval, 'np': np, 'data1': data1, 'sn': sn, 'snval': snval, 'nn': nn, 'data2': data2, 'matrix12': matrix12, "title_matrix12": titlematrix12,
                   'ic': ic, 'id': id, 'iap': iap, 'ian': ian, 'ip': ip, 'ipval':ipval, 'imp': imp, 'data3': data3, 'in': iN, 'inval': inval, 'imn': imn, 'data4': data4,
                   'matrix34': matrix34, 'title_matrix34': titlematrix34, 'ipp': ipp, 'ipn': ipn, 'teacher': teacherProfile, 'testName': test.nombre, 'date': test.date_created.strftime('%d/%m/%Y %H:%M'), 'year': year, 'initials': alumnosInitials})


def show_tests(request, clase, year):
    info = dict()
    teacher = User.objects.get(username=request.user)
    teacherprofile = UserProfile.objects.get(user__username=request.user)
    tests = Test.objects.filter(teacher=teacher, clase=clase)
    for num,test in enumerate(tests):
        alumnos = AlumnoTests.objects.filter(idTest=test)
        alumnos_test = []
        for alumno in alumnos:
            alumnos_test.append(alumno)
        info[num] = {test: alumnos_test}
    if 'download' in request.path:
        confirm = 1
    else:
        confirm = 0
    if 'upload' in request.path:
        confirmUp = 1
    else:
        confirmUp = 0
    return render(request, 'cuestionarios/test_list.html', {"info": info, 'confirm': confirm, 'confirmUp':confirmUp, 'year':year, 'eva': teacherprofile.evaluacion})

@register.filter(is_safe=True)
def is_numeric(value):
    return "{}".format(value).isdigit()

@register.filter
def return_tipo_pregunta(l, i):
    try:
        return l[i-1].pregunta.tipo_pregunta.descripcion
    except:
        return None

@register.filter
def not_empty(l):
    try:
        for num in l:
            for ex in l[num]:
                for innum in l[num][ex]:
                    for inname in l[num][ex][innum]:
                        for ans in l[num][ex][innum][inname]:
                            return True
        return False
    except:
        return None

@register.filter
def return_des(l):
    try:
        for num in l:
            for ex in l[num]:
                for innum in l[num][ex]:
                    for inname in l[num][ex][innum]:
                        for ans in l[num][ex][innum][inname]:
                            return l[num][ex][innum][inname][ans][1]
                                
        return None
    except:
        return None

@register.filter
def not_empty_ex(l):
    try:
        for innum in l:
            for inname in l[innum]:
                for ans in l[innum][inname]:
                    return True
        return False
    except:
        return None

@register.filter
def return_pregunta(l, i):
    try:
        return gettext(l[i-1].pregunta.pregunta.strip())
    except:
        return None

@register.filter
def return_value(l, value):
    for al in l:
        for color in l[al]:
            if l[al][color] != '':
                if int(l[al][color]) == value:
                    alumno = AlumnoTests.objects.get(username=al)
                    return alumno.get_nombre() + " " + alumno.get_apellidos()
    return ''

@register.filter
def return_text(l, value):
    for al in l:
        for color in l[al]:
            if l[al][color] != '':
                if int(l[al][color]) == value:
                    return al
    return ''


def get_t(a, inf):
    aAprox = float(round(a, 1))
    if inf:
        if aAprox == 0.0:
            t = -1.64
        elif aAprox == 0.1:
            t = -1.62
        elif aAprox == 0.2:
            t = -1.59
        elif aAprox == 0.3:
            t = -1.56
        elif aAprox == 0.4:
            t = -1.52
        elif aAprox == 0.5:
            t = -1.49
        elif aAprox == 0.6:
            t = -1.46
        elif aAprox == 0.7:
            t = -1.42
        elif aAprox == 0.8:
            t = -1.39
        elif aAprox == 0.9:
            t = -1.35
        elif aAprox == 1.0:
            t = -1.32
        else:
            t = -1.28
    else:
        if aAprox == 0.0:
            t = 1.64
        elif aAprox == 0.1:
            t = 1.67
        elif aAprox == 0.2:
            t = 1.7
        elif aAprox == 0.3:
            t = 1.73
        elif aAprox == 0.4:
            t = 1.75
        elif aAprox == 0.5:
            t = 1.77
        elif aAprox == 0.6:
            t = 1.8
        elif aAprox == 0.7:
            t = 1.82
        elif aAprox == 0.8:
            t = 1.84
        elif aAprox == 0.9:
            t = 1.86
        elif aAprox == 1.0:
            t = 1.88
        else:
            t = 1.89
    return t
