import requests
import time
import json

from django.contrib.auth.hashers import make_password

from alumnos.models import Clase, Alumno
from cuestionarios.models import Preguntas_test, AlumnoTests, Test
from django.conf import settings 
import errno
from socket import error as socket_error

import logging
log = logging.getLogger(__name__)


def upload_to_server(cuestionario, form):

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

# +++++++++++++++++ Filtrado de los datos para subir al servidor +++++
    clase = Clase.objects.get(nombre=cuestionario.clase)
    alumnos = Alumno.objects.filter(clase_id=clase)
    preguntas = Preguntas_test.objects.filter(test=cuestionario)

# ++++++++++++++++ API ++++++++++++++++++++++++++++++++++++++++
# ++++++++++++++++ Crear test ++++++++++++++++++++++++++++++++++++
    if cuestionario.first:
        result_test = requests.post(
            "https://{0}:{1}/api/test/".format(settings.SERVER_IP, settings.SERVER_PORT),
            data={"nombre": cuestionario.nombre, "first": cuestionario.first.remote_id},
            headers={'Accept': 'application/json',
                    'Authorization': 'Token {}'.format(token)}, verify=False)
    else:
        result_test = requests.post(
            "https://{0}:{1}/api/test/".format(settings.SERVER_IP, settings.SERVER_PORT),
            data={"nombre": cuestionario.nombre, "first": 0},
            headers={'Accept': 'application/json',
                    'Authorization': 'Token {}'.format(token)}, verify=False)
    result_json = json.loads(result_test.content)
    test_server_id = result_json.get('id')


# ++++++++++++++++ Crear preguntas del test ++++++++++++++++++++++++++++++++++++

    for pregunta in preguntas:
        result = requests.post(
            "https://{0}:{1}/api/preguntastests/".format(settings.SERVER_IP, settings.SERVER_PORT),
            data={"test": test_server_id, "pregunta": pregunta.pregunta_id},
            headers={'Accept': 'application/json',
                     'Authorization': 'Token {}'.format(token)}, verify=False)

# +++++++++++++++++++ Crear alumnos +++++++++++++++++++++++++++++++++++++
    for alumno in alumnos:
        username = str(test_server_id) + "-" + str(alumno.id)
        password = make_password("api_user")
        result = requests.post(
            "https://{0}:{1}/api/users/".format(settings.SERVER_IP, settings.SERVER_PORT),
            data={"username": username, "nombre": alumno.nombre,
                  "apellidos": alumno.apellidos, "password": password,
                  "alias": alumno.alias, "test": test_server_id},
            headers={'Accept': 'application/json',
                     'Authorization': 'Token {}'.format(token)}, verify=False)
        al = AlumnoTests()
        al.username = username
        al.idAl = alumno
        al.idTest = cuestionario
        al.save()
    
    cuestionario.remote_id = test_server_id
    cuestionario.uploaded = True
    cuestionario.save()
    clase.modify = False
    clase.save()

def delete_from_server(cuestionario, form, delete):

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

    if cuestionario.first:
        requests.delete(
            "https://{0}:{1}/api/test/".format(settings.SERVER_IP, settings.SERVER_PORT),
            data={"nombre": cuestionario.nombre, "survey": cuestionario.survey2},
            headers={'Accept': 'application/json',
                    'Authorization': 'Token {}'.format(token)}, verify=False)
    else:
        requests.delete(
            "https://{0}:{1}/api/test/".format(settings.SERVER_IP, settings.SERVER_PORT),
            data={"nombre": cuestionario.nombre, "survey": cuestionario.survey1},
            headers={'Accept': 'application/json',
                    'Authorization': 'Token {}'.format(token)}, verify=False)

    if not delete:
        cuestionario.closed = True
        cuestionario.save()

def send_survey1_server(cuestionario, form):

    if not cuestionario.closed:
        result = requests.post(
        "https://193.146.210.219:5050/AtopaServer/api/test",
        json={"id": cuestionario.remote_id},
        headers={'Accept': 'application/json',
                'Authorization': 'Basic YXRvcGFhcHA6YXRvcGExMjNhcHA='}, verify=False)
        log.info(result.content)
        if result.status_code != 200:
            return 1
    
    result = requests.post(
        "https://193.146.210.219:5050/AtopaServer/api/encuesta1",
        json={"test": cuestionario.remote_id, "1": form.cleaned_data['answer1'], "2": form.cleaned_data['answer2'], "3": form.cleaned_data['answer3'], "4": form.cleaned_data['answer4'],
        "5": form.cleaned_data['answer5'], "6": form.cleaned_data['answer6'], "7": form.cleaned_data['answer7'], "8": form.cleaned_data['answer8'], "9": form.cleaned_data['answer9'],
        "10": form.cleaned_data['answer10'], "11": form.cleaned_data['answer11'], "12": form.cleaned_data['answer12'], "13": form.cleaned_data['answer13'], "14": form.cleaned_data['answer14'], "15": form.cleaned_data['answer15']},
        headers={'Accept': 'application/json',
                 'Authorization': 'Basic YXRvcGFhcHA6YXRvcGExMjNhcHA='}, verify=False)
    log.info(result.content)
    if result.status_code != 200:
        return 1
    
    cuestionario.survey1 = True
    cuestionario.save()

def send_survey2_server(cuestionario, form):

    if not cuestionario.closed:
        if cuestionario.first:
            result = requests.post(
            "https://193.146.210.219:5050/AtopaServer/api/test",
            json={"id": cuestionario.remote_id, "first": cuestionario.first.remote_id},
            headers={'Accept': 'application/json',
                    'Authorization': 'Basic YXRvcGFhcHA6YXRvcGExMjNhcHA='}, verify=False)
            log.info(result.content)
            if result.status_code != 200:
                return 1

    result = requests.post(
        "https://193.146.210.219:5050/AtopaServer/api/encuesta2", #193.146.210.219:5050
        json={"test": cuestionario.remote_id, "1": form.cleaned_data['answer1'], "2": form.cleaned_data['answer2'], "3": form.cleaned_data['answer3'], "4": form.cleaned_data['answer4'],
        "5": form.cleaned_data['answer5'], "6": form.cleaned_data['answer6'], "7": form.cleaned_data['answer7'], "8": form.cleaned_data['answer8'], "9": form.cleaned_data['answer9'],
        "10": form.cleaned_data['answer10'], "11": form.cleaned_data['answer11'], "12": form.cleaned_data['answer12'], "13": form.cleaned_data['answer13'], "14": form.cleaned_data['answer14'], 
        "15": form.cleaned_data['answer15'], "16": form.cleaned_data['answer16'], "17": int(form.cleaned_data['answer17']), "18": form.cleaned_data['answer18'], "19": int(form.cleaned_data['answer19'])},
        headers={'Accept': 'application/json',
                 'Authorization': 'Basic YXRvcGFhcHA6YXRvcGExMjNhcHA='}, verify=False)
    log.info(result.content)
    if result.status_code != 200:
        return 1
    
    cuestionario.survey2 = True
    cuestionario.save()