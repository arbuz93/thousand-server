from django.conf.urls import url, include
from user import views

urlpatterns = [
    url(r'^sign_in/$', views.Sign_In.Launch, name='user.sign_in'),
    url(r'^sign_up/$', views.Sign_Up.Launch, name='user.sign_up'),
    url(r'^online/$', views.Get_Online_Users.Launch, name='user.online'),
]
