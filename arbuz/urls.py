from django.conf.urls import url, include

urlpatterns = [
    url(r'^user/', include('user.urls'), name='user'),
    url(r'^game/', include('game.urls'), name='game'),
]

