from django.conf.urls import url
from django.http import HttpResponseRedirect
from . import views

urlpatterns = [
    url(r'^$', lambda r: HttpResponseRedirect('games')),
    url(r'^login/$', views.login),
    url(r'^signup/$', views.signup),
    url(r'^logout/$', views.logout),
    url(r'^games/$', views.games),
    url(r'^play/$', views.play),
]
