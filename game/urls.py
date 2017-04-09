from django.conf.urls import url
from game import views


urlpatterns = [
    url(r'^create/$', views.Create_Game.Launch, name='game.create'),
    url(r'^finish/$', views.Finish_Game.Launch, name='game.finish'),
    url(r'^bidding/$', views.Bidding_Manager.Launch, name='game.bidding'),
    url(r'^status/$', views.Check_Status_Game.Launch, name='game.status'),
    url(r'^chat/$', views.Chat_Manager.Launch, name='game.chat'),
]

