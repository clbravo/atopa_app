import requests
import time
import json

from django.contrib.auth.hashers import make_password

from .models import Respuesta
from cuestionarios.models import Preguntas_test, AlumnoTests, Pregunta
from alumnos.models import Alumno
from django.conf import settings
import logging
log = logging.getLogger(__name__)


def download_from_server(cuestionario, form):

# ++++++++++++++++++ Obtencion de token ++++++++++++++++++++++++++++++

    log.info("Autenticacion en servidor")
    username = form.cleaned_data['username']
    password = form.cleaned_data['password']
    result = requests.post(
        "https://{0}:{1}/api-token-auth/".format(settings.SERVER_IP, settings.SERVER_PORT),
        data={"username": username, "password": password},
        headers={'Accept': 'application/json'}, verify=False)

    log.error(result.content)
    if result.status_code != 200:
        return 1

    result_json = json.loads(result.content)
    token = result_json.get('token')
    students = AlumnoTests.objects.filter(idTest=cuestionario)
    questions = Preguntas_test.objects.filter(test_id=cuestionario)
    for que in questions:
        for student in students:
            Respuesta.objects.filter(pregunta_id=que, alumno_id=student.idAl).delete()

    noresult = True
    for student in students:
        result = requests.get(
            "https://{0}:{1}/api/respuestas?username={2}".format(settings.SERVER_IP, settings.SERVER_PORT,student.username),
            headers={'Accept': 'application/json',
                     'Authorization': 'Token {}'.format(token)}, verify=False)
        if result:
            result_json = json.loads(result.content)

            log.debug(result_json.get("results"))

            respuestas = result_json.get("results")
            if len(respuestas) > 0:
                noresult = False
                student.answer = True
                student.save()
            for element in respuestas:
                res = Respuesta()
                res.alumno = Alumno.objects.get(id=student.idAl.id)
                question = Pregunta.objects.get(id=element.get("question_id"))
                res.pregunta = Preguntas_test.objects.get(test=cuestionario, pregunta=question)
                res.respuesta = element.get('respuesta_username')
                res.save()
    if not noresult:
        cuestionario.downloaded = True
        cuestionario.save()

