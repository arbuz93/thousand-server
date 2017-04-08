from django.conf.urls import url
from game import views


urlpatterns = [
    url(r'^create/$', views.Create_Game.Launch, name='game.create'),
    url(r'^chat/$', views.Chat_Manager.Launch, name='game.chat'),
    url(r'^status/$', views.Check_Status_Game.Launch, name='game.status'),
]
