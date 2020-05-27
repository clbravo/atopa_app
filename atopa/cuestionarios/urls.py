from django.conf.urls import url
from django.urls import reverse_lazy
from cuestionarios import views
from django.contrib.auth.decorators import login_required

urlpatterns = [
    url(r'crear_test/(?P<id>\d+)$', views.crear_test, name='crear_test'),
    url(r'crear_preguntas_test/(?P<clase>\d+)/(?P<estructura>\d+)/(?P<id>\d+)$',
        views.crear_preguntas_test,
        name='crear_preguntas_test'),
    url(r'edittest/(?P<id>\d+)/(?P<year>\d+)$',
        login_required(views.TestUpdate.as_view(success_url=reverse_lazy("testlist"))),
        name='testupdate'),
    url(r'secondtest/(?P<id>\d+)/(?P<year>\d+)$',
        views.secondTest,
        name='secondtest'),
    url(r'survey1/(?P<id>\d+)/(?P<year>\d+)$',
        views.survey1,
        name='survey1'),
    url(r'survey2/(?P<id>\d+)/(?P<year>\d+)$',
        views.survey2,
        name='survey2'),
    url(r'preguntasupdate/(?P<id>\d+)/(?P<year>\d+)$',
        views.update_preguntas_test,
        name='preguntastestupdate'),
    url(r'deletetest/(?P<id>\d+)/(?P<year>\d+)$', views.testDelete,
        name='testdelete'),
    url(r'closetest/(?P<id>\d+)/(?P<year>\d+)$', views.testClose,
        name='testclose'),
    url(r'uploadtest/(?P<id>\d+)/(?P<year>\d+)$',
        views.testupload,
        name='testupload'),
    url(r'downloadtest/(?P<id>\d+)/(?P<year>\d+)$',
        views.testdownload,
        name='testdownload'),
    url(r'codedownload/(?P<id>\d+)$', views.codedownload, name='codedownload'),
    url(r'(?P<id>\d+)$', views.ListAll, name='testlist'),

]
