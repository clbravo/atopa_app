import requests
import time
import json

from django.conf import settings 
import errno
from socket import error as socket_error

import logging
log = logging.getLogger(__name__)

def change_eva(teacher, form, eva):

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

    result_test = requests.put(
            "https://{0}:{1}/api/user/".format(settings.SERVER_IP, settings.SERVER_PORT),
            data={"eva": eva},
            headers={'Accept': 'application/json',
                    'Authorization': 'Token {}'.format(token)}, verify=False)