# -*- coding: utf-8 -*-
from arbuz.views import *
from game.models import *


class Start(Dynamic_Event_Manager):

    def Manage_Game(self):
        return JsonResponse({'Hurra': '!!!'})

    @staticmethod
    def Launch(request):
        return Start(request).HTML


