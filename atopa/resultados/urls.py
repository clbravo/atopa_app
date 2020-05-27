from django.conf.urls import url

from resultados import views

urlpatterns = [
    url(r'^test/(?P<test>\d+)/(?P<year>\d+)$', views.show_results, name='resultados'),
    url(r'^testTodosPdf/(?P<test>\d+)/(?P<year>\d+)$', views.show_results_all, name='resultadosTodosPdf'),
    url(r'^testCompleto/(?P<test>\d+)/(?P<year>\d+)$', views.show_results_complete, name='resultadosCompletos'),
    url(r'^testCompletoPdf/(?P<test>\d+)/(?P<year>\d+)$', views.show_results_complete, name='resultadosCompletosPdf'),
    url(r'^testAlumno/(?P<test>\d+)/(?P<alumno>.+)/(?P<year>\d+)$', views.show_results_student, name='resultadosAlumno'),
    url(r'^testAlumnoPdf/(?P<test>\d+)/(?P<alumno>.+)/(?P<year>\d+)$', views.show_results_student, name='resultadosAlumnoPdf'),
    url(r'(?P<clase>\d+)/(?P<year>\d+)$', views.show_tests, name='tests'),

]
