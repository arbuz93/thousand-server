from django.shortcuts import render
from django.core.urlresolvers import reverse, resolve
from django.http import JsonResponse, HttpResponse
from django.utils.timezone import datetime, timedelta
from django.contrib.auth.hashers import make_password
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.db.models import Q

from arbuz.settings import *
from PIL import Image
from io import BytesIO
from urllib.request import urlopen
from datetime import date
import base64, imghdr, os, string, random, time


class Dynamic_Base:

    def Clear_Session(self, key_contain=''):

        keys = list(self.request.session.keys())
        for key in keys:
            if key_contain in key:
                del self.request.session[key]

    def Get_Urls(self, name=None, kwargs=None):

        if not name:
            name = resolve(self.request.path_info).url_name
            kwargs = resolve(self.request.path_info).kwargs

        secure = 'https://' if self.request.is_secure() else 'http://'
        domain = self.request.get_host()

        return secure + domain + reverse(
            name, urlconf='arbuz.urls', kwargs=kwargs)

    def Get_Path(self, name=None, kwargs=None):

        if not name:
            name = resolve(self.request.path_info).url_name
            kwargs = resolve(self.request.path_info).kwargs

        return reverse(name, urlconf='arbuz.urls', kwargs=kwargs)

    @staticmethod
    def Generate_Passwrod(length):
        password = ''
        permitted_chars = string.ascii_letters + \
                          string.digits + \
                          string.punctuation

        for char_number in range(0, length):
            password += random.choice(permitted_chars)

        return password

    @staticmethod
    def Convert_Polish_To_Ascii(text):

        characters = {
            'ą': 'a', 'ć': 'c', 'ę': 'e',
            'ł': 'l', 'ń': 'n', 'ó': 'o',
            'ś': 's', 'ź': 'z', 'ż': 'z',

            'Ą': 'A', 'Ć': 'C', 'Ę': 'E',
            'Ł': 'L', 'Ń': 'N', 'Ó': 'O',
            'Ś': 'S', 'Ź': 'Z', 'Ż': 'Z',
        }

        text_ascii = ''
        for char in text:
            if char in characters:
                char = characters[char]

            text_ascii += char

        return text_ascii

    @staticmethod
    def Encrypt(password):
        return make_password(password=password, salt='arbuz-team')

    @staticmethod
    def Get_Text_Cell(text, spaces=20, margin=0):
        spaces = ' ' * (spaces - len(text) - margin)
        margin = ' ' * margin
        return margin + text + spaces

    def Timer_Start(self):

        if DEBUG:
            self.start_time = time.time()

    def Display_Status(self, message=None):

        if DEBUG:

            if not DISPLAY_STATUS and not message:
                return

            status = '-' * 125 + '\n\n'
            status += self.Get_Text_Cell('Application: ')
            status += self.app_name

            if message: status += ' ({0}) \n\n'.format(message)
            else: status += '\n\n'

            duration = time.time() - self.start_time
            duration = str(int(duration * 1000))
            status += self.Get_Text_Cell('Duration: ', margin=2)
            status += duration + ' ms\n'

            status += self.Get_Text_Cell('URL: ', margin=2)
            status += self.Get_Path() + '\n'

            if self.request.POST:

                variables = []
                status += self.Get_Text_Cell('POST: ', margin=2)

                for key in self.request.POST:

                    variables.append(
                        self.Get_Text_Cell(key, 30) +
                        str(self.request.POST[key])
                    )

                separator = '\n' + self.Get_Text_Cell('')
                status += separator.join(variables) + '\n'

            keys = self.request.session.keys()
            if any(key.startswith(self.app_name) for key in keys):

                variables = []
                status += self.Get_Text_Cell('Session: ', margin=2)

                for key in keys:
                    if key.startswith(self.app_name):

                        variables.append(
                            self.Get_Text_Cell(key, 30) +
                            str(self.request.session[key])
                        )

                separator = '\n' + self.Get_Text_Cell('')
                status += separator.join(variables) + '\n'

            status += '\n' + '-' * 125 + '\n'
            print(status)

    def __init__(self, request):

        self.request = request
        self.start_time = 0
        self.content = {}

        last_dot = self.__module__.rfind('.')
        self.app_name = self.__module__[:last_dot]
