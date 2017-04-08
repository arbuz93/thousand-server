from arbuz.views import *
from user.models import *


class Sign_In(Dynamic_Event_Manager):

    def Manage_Game(self):

        username = self.request.POST['username']
        password = self.request.POST['password']

        if not username or not password:
            return JsonResponse({'status': False})

        if User.objects.filter(username=username):
            user = User.objects.get(username=username)

            if user.password == self.Encrypt(password):
                self.request.session['user_username'] = username
                self.request.session['user_login'] = True
                user.online = True
                user.save()

                return JsonResponse({'status': True})
        return JsonResponse({'status': False})

    @staticmethod
    def Launch(request):
        return Sign_In(request).JSON



class Sign_Up(Dynamic_Event_Manager):

    def Manage_Game(self):

        username = self.request.POST['username']
        password = self.request.POST['password']

        if not username or not password:
            return JsonResponse({'status': False})

        if not User.objects.filter(username=username):

            User(
                username=username,
                password=self.Encrypt(password),
                online=False
            ).save()

            return JsonResponse({'status': True})
        return JsonResponse({'status': False})

    @staticmethod
    def Launch(request):
        return Sign_Up(request).JSON



class Get_Online_Users(Dynamic_Event_Manager):

    def Manage_Game(self):
        users = User.objects.filter(online=True).values('username')
        return JsonResponse({'users': list(users)})

    @staticmethod
    def Launch(request):
        return Get_Online_Users(request, authorization=True).JSON

