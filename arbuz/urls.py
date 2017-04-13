from django.conf.urls import url, include

urlpatterns = [
    url(r'', include('init.urls'), name='init'),
    url(r'^user/', include('user.urls'), name='user'),
    url(r'^game/', include('game.urls'), name='game'),
    url(r'^status/', include('status.urls'), name='status'),
    url(r'^chat/', include('chat.urls'), name='chat'),
]

