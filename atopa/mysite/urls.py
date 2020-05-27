"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin
from django.conf import settings
from django.views.generic import TemplateView

import os

PROJECT_DIR = os.path.dirname(__file__)
urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^accounts/', include('django.contrib.auth.urls')),
    # url(r'^login/', TemplateView.as_view(template_name='login.html')),
    url(r'alumnos/', include('alumnos.urls')),
    url(r'cuestionarios/', include('cuestionarios.urls')),
    url(r'resultados/', include('resultados.urls')),
    url(r'^i18n/', include('django.conf.urls.i18n')),
    url(r'', include('teacher.urls')),
]
