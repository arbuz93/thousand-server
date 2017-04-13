from django.conf.urls import url
from game import views


urlpatterns = [
    url(r'^create/$', views.Create_Game.Launch, name='game.create'),
    url(r'^finish/$', views.Finish_Game.Launch, name='game.finish'),
    url(r'^bidding/$', views.Bidding_Manager.Launch, name='game.bidding'),
    url(r'^throw_card/$', views.Throw_Card.Launch, name='game.throw_card'),
    url(r'^game_users/$', views.Get_Game_Users.Launch, name='game.game_users'),
]

