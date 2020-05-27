from django.conf.urls import url
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from alumnos import views

urlpatterns = [
    url(r'edit/(?P<id>\d+)/(?P<year>\d+)$',
        login_required(views.AlumnoUpdate.as_view(success_url=reverse_lazy("estudiantes"))),
        name='alumnoupdate'),
    url(r'crear_alumno/(?P<year>\d+)$', views.crear_alumno, name='crear_alumno'),
    url(r'importar_alumnos/(?P<year>\d+)$', views.importar_alumnos, name='importar_alumnos'),
    url(r'crear_clase/(?P<year>\d+)$', views.crear_clase, name='crear_clase'),
    url(r'editclase/(?P<id>\d+)/(?P<year>\d+)$',
        login_required(views.ClaseUpdate.as_view(success_url=reverse_lazy("estudiantes"))),
        name='claseupdate'),
    url(r'editclase2/(?P<id>\d+)/(?P<year>\d+)$',
        login_required(views.ClaseUpdate2.as_view(success_url=reverse_lazy("estudiantes"))),
        name='claseupdate2'),
    url(r'deleteclase/(?P<id>\d+)/(?P<year>\d+)$',
        views.claseDelete,
        name='clasedelete'),
    url(r'deletealumno/(?P<id>\d+)/(?P<year>\d+)$',
        login_required(views.AlumnoDelete.as_view(success_url=reverse_lazy("estudiantes"))),
        name='alumnodelete'),
    url(r'serverdown/(?P<year>\d+)$', views.noserver, name='noservertest'),
    url(r'(?P<id>\d+)$', views.ListAll, name='estudiantes'),
]
