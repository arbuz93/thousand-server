from arbuz.views import *
from chat.models import *


class Chat_Manager(Dynamic_Event_Manager):

    def Add_Message(self):
        game = Game.objects.get(pk=self.request.session['game_pk'])
        user = User.objects.get(username=self.request.session['user_username'])
        message = self.request.POST['message']
        Chat(message=message, game=game, user=user).save()
        return JsonResponse({'status': True})

    @staticmethod
    def Get_Messages(game_pk):

        # game not created
        if not Game.objects.filter(pk=game_pk):
            return []

        game = Game.objects.get(pk=game_pk)
        messages = Chat.objects.filter(game=game)\
            .values('message', 'user', 'date')

        return list(messages)[-8:]

    def Manage_Game(self):

        if not self.request.session['game_pk']:
            return JsonResponse({'status': False})

        return self.Add_Message()

    @staticmethod
    def Launch(request):
        return Chat_Manager(request, authorization=True, game_exists=True).JSON