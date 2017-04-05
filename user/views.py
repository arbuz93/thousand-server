from arbuz.views import *
import os, binascii


class Sign_In(Dynamic_Event_Manager):

    @staticmethod
    def Launch(request):
        return Sign_In(request).HTML



class Sign_Up(Dynamic_Event_Manager):

    @staticmethod
    def Launch(request):
        return Sign_Up(request).HTML



class Sign_Out(Dynamic_Event_Manager):

    @staticmethod
    def Launch(request):
        return Sign_Out(request, authorization=True).HTML

