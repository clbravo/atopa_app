# -*- coding: utf-8 -*-
from django import forms
import requests
from django.core.exceptions import ValidationError
from django.utils.translation import gettext
from django.conf import settings
from django.utils.safestring import mark_safe
import logging
import json
log = logging.getLogger(__name__)


class LoginUploadForm(forms.Form):
    username = forms.CharField(max_length=60)
    password = forms.CharField(max_length=20, widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super(LoginUploadForm, self).__init__(*args, **kwargs)
        self.fields['username'].label = gettext('Usuario servidor')
        self.fields['password'].label = gettext('Contraseña servidor')

    def clean(self):
        cleaned_data = self.cleaned_data
        username = self.data['username']
        password = self.data['password']
        result = requests.post(
            "https://{0}:{1}/api-token-auth/".format(settings.SERVER_IP, settings.SERVER_PORT),
            data={"username": username, "password": password},
            headers={'Accept': 'application/json'}, verify=False)
        if result.status_code != 200:
            result_json = json.loads(result.content)
            raise ValidationError(result_json.get("non_field_errors")[0])
        return cleaned_data


class Survey1Form(forms.Form):
    choices1 = ((gettext('Orientador/a'), gettext('Orientador/a')), (gettext('Profesor/a'), gettext('Profesor/a')), (gettext('Psicólogo/a'), gettext('Psicólogo/a')))
    answer1 = forms.ChoiceField(required=True, choices=choices1, widget=forms.RadioSelect())
    choices2 = ((gettext('<30'), gettext('<30')), (gettext('30-45'), gettext('30-45')), (gettext('46-60'), gettext('46-60')), (gettext('>60'), gettext('>60')), (gettext('Prefieron no contestar'), gettext('Prefiero no contestar')))
    answer2 = forms.ChoiceField(required=True, choices=choices2, widget=forms.RadioSelect())
    choices3 = ((gettext('Mujer'), gettext('Mujer')), (gettext('Hombre'), gettext('Hombre')), (gettext('Prefieron no contestar'), gettext('Prefiero no contestar')))
    answer3 = forms.ChoiceField(required=True, choices=choices3, widget=forms.RadioSelect())
    choices4 = ((gettext('Sí'), gettext('Sí')), (gettext('No'), gettext('No')), (gettext('NS/NC'), gettext('NS/NC')))
    answer4 = forms.ChoiceField(required=True, choices=choices4, widget=forms.RadioSelect())
    answer5 = forms.ChoiceField(required=True, choices=choices4, widget=forms.RadioSelect())
    answer6 = forms.ChoiceField(required=True, choices=choices4, widget=forms.RadioSelect())
    answer7 = forms.ChoiceField(required=True, choices=choices4, widget=forms.RadioSelect())
    answer8 = forms.ChoiceField(required=True, choices=choices4, widget=forms.RadioSelect())
    answer9 = forms.ChoiceField(required=True, choices=choices4, widget=forms.RadioSelect())
    answer10 = forms.ChoiceField(required=True, choices=choices4, widget=forms.RadioSelect())
    answer11 = forms.ChoiceField(required=True, choices=choices4, widget=forms.RadioSelect())
    answer12 = forms.ChoiceField(required=True, choices=choices4, widget=forms.RadioSelect())
    answer13 = forms.ChoiceField(required=True, choices=choices4, widget=forms.RadioSelect())
    answer14 = forms.ChoiceField(required=True, choices=choices4, widget=forms.RadioSelect())
    answer15 = forms.ChoiceField(required=True, choices=choices4, widget=forms.RadioSelect())

    def __init__(self, *args, **kwargs):
        super(Survey1Form, self).__init__(*args, **kwargs)
        self.fields['answer1'].label = gettext('Por favor, indique a qué grupo pertenece')
        self.fields['answer2'].label = gettext('Por favor, indique su rango de edad')
        self.fields['answer3'].label = gettext('Por favor, indique su sexo')
        self.fields['answer4'].label = gettext('¿El alumno o alumna líder positivo del grupo que usted esperaba coincide con el resultado del informe?')
        self.fields['answer5'].label = gettext('¿El alumno o alumna líder negativo del grupo que usted esperaba coincide con el resultado del informe?')
        self.fields['answer6'].label = gettext('¿Los alumnos o alumnas rechazados por sus compañeros que usted esperaba coinciden con el resultado del informe?')
        self.fields['answer7'].label = gettext('¿Los alumnos o alumnas aislados que usted esperaba coinciden con el resultado del informe?')
        self.fields['answer8'].label = gettext('¿Los alumnos o alumnas que comparten una relación de amistad/enemistad mutua que usted esperaba coinciden con el resultado del informe?')
        self.fields['answer9'].label = gettext('¿Los alumnos o alumnas con los que sus compañeros no quieren trabajar en grupo que usted esperaba coinciden con el resultado del informe?')
        self.fields['answer10'].label = gettext('Las situaciones sociales en este grupo que considera que convendría mejorar coinciden con la propuesta de intervención del informe')
        self.fields['answer11'].label = gettext('Antes de realizar el cuestionario ¿pensaba que el grupo estaba cohesionado?')
        self.fields['answer12'].label = gettext('¿Ha cambiado su opinión después de hacer el cuestionario?')
        self.fields['answer13'].label = gettext('Antes de realizar el cuestionario ¿pensaba que había subgrupos en el aula?')
        self.fields['answer14'].label = gettext('¿Ha cambiado su opinión después de hacer el cuestionario?')
        self.fields['answer15'].label = gettext('¿Los subgrupos que usted esperaba que hubiese en el aula, coinciden con los identificados en el informe?')

class Survey2Form(forms.Form):
    choices1 = ((gettext('Orientador/a'), gettext('Orientador/a')), (gettext('Profesor/a'), gettext('Profesor/a')), (gettext('Psicólogo/a'), gettext('Psicólogo/a')))
    answer1 = forms.ChoiceField(required=True, choices=choices1, widget=forms.RadioSelect())
    choices2 = ((gettext('<30'), gettext('<30')), (gettext('30-45'), gettext('30-45')), (gettext('46-60'), gettext('46-60')), (gettext('>60'), gettext('>60')), (gettext('Prefieron no contestar'), gettext('Prefiero no contestar')))
    answer2 = forms.ChoiceField(required=True, choices=choices2, widget=forms.RadioSelect())
    choices3 = ((gettext('Mujer'), gettext('Mujer')), (gettext('Hombre'), gettext('Hombre')), (gettext('Prefieron no contestar'), gettext('Prefiero no contestar')))
    answer3 = forms.ChoiceField(required=True, choices=choices3, widget=forms.RadioSelect())

    choices4 = ((gettext('Sí'), gettext('Sí')), (gettext('No'), gettext('No')), (gettext('NS/NC'), gettext('NS/NC')))
    answer4 = forms.ChoiceField(required=True, choices=choices4, widget=forms.RadioSelect())
    answer5 = forms.ChoiceField(required=True, choices=choices4, widget=forms.RadioSelect())
    answer6 = forms.ChoiceField(required=True, choices=choices4, widget=forms.RadioSelect())
    answer7 = forms.ChoiceField(required=True, choices=choices4, widget=forms.RadioSelect())
    answer8 = forms.ChoiceField(required=True, choices=choices4, widget=forms.RadioSelect())
    answer9 = forms.CharField(required=False, max_length=200, widget=forms.Textarea(attrs={"rows":8, "cols":45}))
    answer10 = forms.CharField(required=True, max_length=200, widget=forms.Textarea(attrs={"rows":8, "cols":45}))
    choices5 = ((gettext('Sí'), gettext('Sí')), (gettext('No'), gettext('No')))
    answer11 = forms.ChoiceField(required=True, choices=choices5, widget=forms.RadioSelect())
    answer12 = forms.ChoiceField(required=True, choices=choices4, widget=forms.RadioSelect())
    answer13 = forms.ChoiceField(required=True, choices=choices4, widget=forms.RadioSelect())
    answer14 = forms.ChoiceField(required=True, choices=choices4, widget=forms.RadioSelect())
    answer15 = forms.ChoiceField(required=True, choices=choices4, widget=forms.RadioSelect())
    choices6 = ((gettext('empeoró alarmantemente'), gettext('empeoró alarmantemente')), (gettext('empeoró ligeramente'), gettext('empeoró ligeramente')), (gettext('se mantuvo'), gettext('se mantuvo')), (gettext('mejoró ligeramente'), gettext('mejoró ligeramente')), (gettext('mejoró sustancialmente'), gettext('mejoró sustancialmente')), (gettext('NS/NC'), gettext('NS/NC')))
    answer16 = forms.ChoiceField(required=True, choices=choices6, widget=forms.RadioSelect())
    choices6 = ((1,1), (2,2), (3,3), (4,4), (5,5), (6,6), (7,7), (8,8), (9,9), (10,10))
    answer17 = forms.ChoiceField(required=True, choices=choices6, widget=forms.RadioSelect())
    answer18 = forms.CharField(required=True, max_length=200, widget=forms.Textarea(attrs={"rows":8, "cols":45}))
    choices7 = ((0,0), (1,1), (2,2), (3,3), (4,4), (5,5), (6,6), (7,7), (8,8), (9,9), (10,10))
    answer19 = forms.ChoiceField(required=True, choices=choices7, widget=forms.RadioSelect())

    def __init__(self, *args, **kwargs):
        super(Survey2Form, self).__init__(*args, **kwargs)
        self.fields['answer1'].label = gettext('Por favor, indique a qué grupo pertenece')
        self.fields['answer2'].label = gettext('Por favor, indique su rango de edad')
        self.fields['answer3'].label = gettext('Por favor, indique su sexo')
        self.fields['answer4'].label = gettext('¿Cree que los resultados de los informes individuales del primer cuestionario son acertados?')
        self.fields['answer5'].label = gettext('¿Cree que los resultados de los informes de grupo del primer cuestionario son acertados?')
        self.fields['answer6'].label = gettext('¿Cree que las propuestas de intervención del primer cuestionario son acertadas?')
        self.fields['answer7'].label = gettext('¿Ha tenido en cuenta los resultados de los informes generados por la aplicación ATOPA para realizar actividades de intervención en el aula?')
        self.fields['answer8'].label = gettext('¿Ha utilizado alguna de las actividades propuestas en la Web Atopa?')
        self.fields['answer9'].label = gettext('En caso de haber utilizado alguna de las actividades propuestas ¿podría decirnos cuáles?')
        self.fields['answer10'].label = gettext('Describa brevemente su experiencia (indique las principales áreas en las que trabajar con el grupo, las actividades llevadas a cabo, la duración del proceso...)')
        self.fields['answer11'].label = gettext('¿Ha realizado un segundo cuestionario?')
        self.fields['answer12'].label = gettext('¿Cree que los resultados de los informes individuales del segundo cuestionario son acertados?')
        self.fields['answer13'].label = gettext('¿Cree que los resultados de los informes de grupo del segundo cuestionario son acertados?')
        self.fields['answer14'].label = gettext('¿Cree que las propuestas de intervención del segundo cuestionario son acertadas?')
        self.fields['answer15'].label = gettext('¿Se ha reducido el número de alumnos que sufre rechazo?')
        self.fields['answer16'].label = gettext('¿Cuál es su percepción sobre la evolución de la convivencia en el aula, desde que se realizó el primer cuestionario, hasta que se realizó el segundo?')
        self.fields['answer17'].label = gettext('Si puntuase la aplicación Atopa en una escala del 1 al 10, ¿qué puntuación nos daría?')
        self.fields['answer18'].label = gettext('En pocas palabras, describa lo que motivó su nota')
        self.fields['answer19'].label = gettext('¿Qué probabilidad hay de que pueda recomendar la aplicación Atopa a sus colegas? (0: Nada probable - 10: Muy probable)')
