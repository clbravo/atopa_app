from django.conf.urls import url
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required

from . import views
from .forms import PasswordForm

urlpatterns = [
    url(r'^register/', views.register, name='register'),
    url(r'^teacherAccount/', views.account, name='teacher'),
    url(r'^evaluate/', views.evaluate, name='evaluate'),
    url(r'^noevaluate/', views.noevaluate, name='noevaluate'),
    url(r'^menu/(?P<id>\d+)$', views.menu,name='menu'),
    url('password-reset-confirm/(?P<uidb64>[^/]+)/(?P<token>[^/]+)/$',auth_views.PasswordResetConfirmView.as_view(
             form_class=PasswordForm
         ),
         name='password_reset_confirm'),
    url(r'^$', views.school_year_list, name='home')
]