# -*- coding: utf-8 -*-
from arbuz.views import *
from game.models import *


class Create_Game(Dynamic_Event_Manager):

    def Manage_Game(self):

        user_1 = self.request.POST['user_1']
        user_2 = self.request.POST['user_2']
        user_3 = self.request.session['user_username']

        if not User.objects.filter(username=user_1):
            return JsonResponse({'status': False})

        if not User.objects.filter(username=user_2):
            return JsonResponse({'status': False})

        game = Game()
        game.save()
        game.users.add(User.objects.get(username=user_1))
        game.users.add(User.objects.get(username=user_2))
        game.users.add(User.objects.get(username=user_3))

        self.request.session['game_pk'] = game.pk
        return JsonResponse({'status': True})

    @staticmethod
    def Launch(request):
        return Create_Game(request, authorization=True).JSON



class Check_Status_Game(Dynamic_Event_Manager):

    def Manage_Game(self):
        username = self.request.session['user_username']

        if Game.objects.filter(users__username=username):
            self.request.session['game_pk'] = Game.objects.filter(
                users__username=username)[0].pk

            return JsonResponse({'status': True})
        return JsonResponse({'status': False})

    @staticmethod
    def Launch(request):
        return Check_Status_Game(request, authorization=True).JSON



class Chat_Manager(Dynamic_Event_Manager):

    def Add_Message(self):
        game = Game.objects.get(pk=self.request.session['game_pk'])
        user = User.objects.get(username=self.request.session['user_username'])
        message = self.request.POST['message']
        Chat(message=message, game=game, user=user).save()
        return JsonResponse({'status': True})

    def Get_All(self):
        game = Game.objects.get(pk=self.request.session['game_pk'])
        messages = Chat.objects.filter(game=game).values('message', 'user', 'date')
        return JsonResponse({'messages': list(messages)})

    def Manage_Game(self):

        if not self.request.session['game_pk']:
            return JsonResponse({'status': False})

        if '__add__' in self.request.POST:
            return self.Add_Message()

        if '__get__' in self.request.POST:
            return self.Get_All()

    @staticmethod
    def Launch(request):
        return Chat_Manager(request, authorization=True).JSON
