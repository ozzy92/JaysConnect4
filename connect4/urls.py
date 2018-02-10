from django.conf.urls import url
from django.urls import path
from django.http import HttpResponseRedirect
from . import views

urlpatterns = [    
    url(r'^$', lambda r: HttpResponseRedirect('games')),    # redirect root to games
    url(r'^login/$', views.login),
    url(r'^signup/$', views.signup),
    url(r'^logout/$', views.logout),
    url(r'^games/', views.games),
    path('play/<int:pk>/', views.play),
]
