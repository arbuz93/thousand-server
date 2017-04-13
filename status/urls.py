from django.conf.urls import url
from status import views


urlpatterns = [
    url(r'^$', views.Check_Status_Game.Launch, name='status'),
]

