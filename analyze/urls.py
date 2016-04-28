from django.conf.urls import url

from . import views

app_name = 'analyze'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^results/$', views.deck, name='deck'),
]
