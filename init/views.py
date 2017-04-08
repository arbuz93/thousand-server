# -*- coding: utf-8 -*-
from arbuz.views import *


class Init(Dynamic_Event_Manager):

    @staticmethod
    def Launch(request):
        return Init(request).JSON
