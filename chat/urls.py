from django.conf.urls import url
from chat import views


urlpatterns = [
    url(r'^$', views.Chat_Manager.Launch, name='chat'),
]

