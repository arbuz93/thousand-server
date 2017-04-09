# -*- coding: utf-8 -*-
from logic.views import *


class Create_Game(Dynamic_Event_Manager):

    def Valid_Data(self):

        user_1 = self.request.POST['user_1']
        user_2 = self.request.POST['user_2']
        user_3 = self.request.session['user_username']

        # username have to unique
        if user_1 == user_2 or user_2 == user_3 or user_3 == user_1:
            return False

        # users exists
        if not User.objects.filter(username=user_1):
            return False

        if not User.objects.filter(username=user_2):
            return False

        return True

    def Manage_Game(self):
        Finish_Game.Finish_Last_Games(self.request)

        user_1 = self.request.POST['user_1']
        user_2 = self.request.POST['user_2']
        user_3 = self.request.session['user_username']

        main_user = User.objects.get(username=user_3)
        game = Game(start_user=main_user, current_user=main_user)

        game.save()
        game.users.add(User.objects.get(username=user_1))
        game.users.add(User.objects.get(username=user_2))
        game.users.add(User.objects.get(username=user_3))

        self.request.session['game_pk'] = game.pk
        Logic.Dealing_Cards(game.pk)

        return JsonResponse({'status': True})

    def Manage(self):

        if not self.Valid_Data():
            return JsonResponse({'status': False})

        return self.Manage_Game()

    @staticmethod
    def Launch(request):
        return Create_Game(request, authorization=True).JSON



class Finish_Game(Dynamic_Event_Manager):

    @staticmethod
    def Finish_Last_Games(request):
        username = request.session['user_username']
        Game.objects.filter(users__username=username).delete()

    def Manage_Game(self):
        self.Finish_Last_Games(self.request)
        return JsonResponse({'status': True})

    @staticmethod
    def Launch(request):
        return Create_Game(request, authorization=True, game_exists=True).JSON



class Bidding_Manager(Dynamic_Event_Manager):

    def Manage_Game(self):

        game = Game.objects.get(pk=self.request.session['game_pk'])
        user = User.objects.get(username=self.request.session['user_username'])
        points = self.request.POST['points']

        # user passing
        if points == 0:

            # change to next user
            game.current_user

            return JsonResponse({})

        # get points are greater than last bidding
        last_match = game.matchs.all()[-1]
        if points > last_match.bidding.score:

            # save new bidding and user
            last_match.bidding.score = points
            last_match.bidding.user = user

            return JsonResponse({'status': True})

        return JsonResponse({'status': False})

    @staticmethod
    def Launch(request):
        return Check_Status_Game(request, authorization=True).JSON



class Check_Status_Game(Dynamic_Event_Manager):

    def Join_To_Game(self):
        username = self.request.session['user_username']
        self.reply['join'] = False

        if Game.objects.filter(users__username=username):
            self.request.session['game_pk'] = Game.objects.filter(
                users__username=username)[0].pk

            self.reply['join'] = True

    def Status_Chat_Messages(self):
        game_pk = self.request.session['game_pk']
        messages = Chat_Manager.Get_Messages(game_pk)
        self.reply['messages'] = messages

    def Status_Assigned_Cards(self):
        username = self.request.session['user_username']
        user = User.objects.get(username=username)
        cards = Assigned_Cards.objects.filter(user=user)\
            .values('cards__color__name', 'cards__rank__name')

        self.reply['cards'] = list(cards)

    def Status_Stock(self):
        game = Game.objects.get(pk=self.request.session['game_pk'])
        stock = Match.objects.filter(game=game)\
            .values('stock__color__name', 'stock__rank__name')

        self.reply['stock'] = list(stock)

    def Manage_Game(self):

        methods = getmembers(self, predicate=ismethod)
        methods = [method[0] for method in methods]

        for method in methods:
            if 'Status_' in method:
                getattr(Check_Status_Game, method)(self)

        return JsonResponse(self.reply)

    def Manage(self):

        self.Join_To_Game()
        if not self.request.session['game_pk']:
            return JsonResponse({'error': 'game_exists'})

        return self.Manage_Game()

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
