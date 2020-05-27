import requests
import time
import json

from django.contrib.auth.hashers import make_password

from alumnos.models import Clase, Alumno
from cuestionarios.models import Preguntas_test, AlumnoTests, Test
from django.conf import settings
import logging
log = logging.getLogger(__name__)


def upload_student_to_server(alumno, form):

    # ++++++++++++++++++ Obtencion de token ++++++++++++++++++++++++++++++

    username = form.cleaned_data['username']
    password = form.cleaned_data['password']
    result = requests.post(
        "https://{0}:{1}/api-token-auth/".format(settings.SERVER_IP, settings.SERVER_PORT),
        data={"username": username, "password": password},
        headers={'Accept': 'application/json'}, verify=False)

    if result.status_code != 200:
        return 1

    result_json = json.loads(result.content)
    token = result_json.get('token')

    tests = Test.objects.filter(clase=alumno.clase_id, closed=False, uploaded=True)

    for t in tests:
        result = requests.get(
            "https://{0}:{1}/api/tests/".format(settings.SERVER_IP, settings.SERVER_PORT),
            headers={'Accept': 'application/json',
                     'Authorization': 'Token {}'.format(token)}, verify=False)
        result_json = json.loads(result.content)
        for re in result_json['results']:
            if re['nombre'] == t.nombre:
                username = str(re['id']) + str(alumno.id)
                password = make_password("api_user")
                result = requests.post(
                    "https://{0}:{1}/api/users/".format(settings.SERVER_IP, settings.SERVER_PORT),
                    data={"username": username, "nombre": alumno.nombre,
                          "apellidos": alumno.apellidos, "password": password,
                          "alias": alumno.alias, "test": re['id']},
                    headers={'Accept': 'application/json',
                             'Authorization': 'Token {}'.format(token)}, verify=False)
                al = AlumnoTests()
                al.username = username
                al.idAl = alumno
                al.idTest = t
                al.save()

def delete_class_from_server(clase, form):

    # ++++++++++++++++++ Obtencion de token ++++++++++++++++++++++++++++++

    username = form.cleaned_data['username']
    password = form.cleaned_data['password']
    result = requests.post(
        "https://{0}:{1}/api-token-auth/".format(settings.SERVER_IP, settings.SERVER_PORT),
        data={"username": username, "password": password},
        headers={'Accept': 'application/json'}, verify=False)

    if result.status_code != 200:
        return 1

    result_json = json.loads(result.content)
    token = result_json.get('token')

    tests = Test.objects.filter(clase=clase, closed=False, uploaded=True)

    for t in tests:
        requests.delete(
            "https://{0}:{1}/api/test/{2}".format(settings.SERVER_IP, settings.SERVER_PORT,t.nombre),
            headers={'Accept': 'application/json',
                     'Authorization': 'Token {}'.format(token)}, verify=False)