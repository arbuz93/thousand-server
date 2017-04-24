# -*- coding: utf-8 -*-
from logic.views import *
from chat.views import *


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

        # get users
        user_0 = self.request.session['user_username']
        user_1 = self.request.POST['user_1']
        user_2 = self.request.POST['user_2']

        user_0 = User.objects.get(username=user_0)
        user_1 = User.objects.get(username=user_1)
        user_2 = User.objects.get(username=user_2)

        # users join to game
        user_0.in_game = True
        user_1.in_game = True
        user_2.in_game = True

        user_0.save()
        user_1.save()
        user_2.save()

        # create game
        game = Game(start_user=user_0)

        game.save()
        game.users.add(User.objects.get(username=user_0))
        game.users.add(User.objects.get(username=user_1))
        game.users.add(User.objects.get(username=user_2))
        game.current_user = game.Get_Next_User(user_0)
        game.save()

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

        if not request.session['game_pk']:
            return

        game = Game.objects.get(pk=request.session['game_pk'])
        request.session['game_pk'] = None

        for user in game.users.all():
            user.in_game = False
            user.save()

        game.delete()

    def Manage_Game(self):
        self.Finish_Last_Games(self.request)
        return JsonResponse({'status': True})

    @staticmethod
    def Launch(request):
        return Finish_Game(request, authorization=True, game_exists=True).JSON



class Bidding_Manager(Dynamic_Event_Manager):

    @staticmethod
    def Get_Biddings(game):
        biddings = game.matchs.last().biddings\
            .values('points', 'user')

        return list(biddings)

    def Manage_Dealing_Stock_Cards(self):

        # [color, rank]
        first_card = self.request.POST['first_card'].split(' ')
        second_card = self.request.POST['second_card'].split(' ')

        first_card = Card.objects.get(
            color__name=first_card[0],
            rank__name=first_card[1])

        second_card = Card.objects.get(
            color__name=second_card[0],
            rank__name=second_card[1])

        # users
        user = self.request.session['user_username']
        first_user = self.request.POST['first_user']
        second_user = self.request.POST['second_user']

        user = User.objects.get(username=user)
        first_user = User.objects.get(username=first_user)
        second_user = User.objects.get(username=second_user)

        # get last match
        pk = self.request.session['game_pk']
        game = Game.objects.get(pk=pk)

        # move cards from stock to user cards
        stock_cards = game.Get_Stock_Card()
        user_cards = Assigned_Cards.objects.get(user=user)
        user_cards.cards.add(*stock_cards)
        user_cards.cards.remove(first_card)
        user_cards.cards.remove(second_card)
        Stock_Card.objects.filter(game=game).delete()

        # move cards from user to first / second user
        Assigned_Cards.objects.get(user=first_user)\
            .cards.add(first_card)

        Assigned_Cards.objects.get(user=second_user)\
            .cards.add(second_card)

        # dealing over
        game.is_dealing = False
        game.save()

        return JsonResponse({'status': True})

    def Manage_Get_Bidding_Cards(self):

        # variable
        pk = self.request.session['game_pk']
        game = Game.objects.get(pk=pk)
        user = Logic.Get_Win_Bidding(game).user

        # get cards
        stock_cards = game.Get_Stock_Card()\
            .values('color__name', 'rank__name')

        assigned_cards = Assigned_Cards.objects.get(user=user)\
            .cards.all().values('color__name', 'rank__name')

        # return
        cards = list(assigned_cards) + list(stock_cards)
        return JsonResponse({'cards': cards})

    def Manage_Add_Bidding(self):

        # variable
        game = Game.objects.get(pk=self.request.session['game_pk'])
        last_match = game.matchs.last()
        points = int(self.request.POST['points'])

        # check points are round to tens
        if points % 10 != 0:
            return JsonResponse({'status': 5}) # not round to tens

        # check if user may to win the points
        username = self.request.session['user_username']
        user = User.objects.get(username=username)
        user_max_points = Logic.Count_User_Max_Points(user, game)
        if points > user_max_points:
            return JsonResponse({'status': 4}) # too big

        # get points are greater than last bidding or user passing
        max_points = Logic.Get_Win_Bidding(game).points

        if points > max_points or points == 0:
            bidding = Bidding(points=points, user=game.current_user)
            bidding.save()

            last_match.biddings.add(bidding)

            # find next user
            next_user = Logic.Find_Next_User(game, last_match)
            if not next_user:
                self.Manage_Finish_Bidding()
                return JsonResponse({'status': 0})

            game.current_user = next_user
            game.save()

            return JsonResponse({'status': 0}) # save
        return JsonResponse({'status': 2}) # to small

    def Manage_Finish_Bidding(self):

        game = Game.objects.get(pk=self.request.session['game_pk'])
        user = User.objects.get(username=self.request.session['user_username'])
        match = game.matchs.last()

        if not Logic.Find_Next_User(game, match):

            # bidding over
            game.is_bidding = False
            game.is_dealing = True
            game.save()

            match.bidded_user = user
            match.save()

            return JsonResponse({'status': 0})

        return JsonResponse({'status': 1}) # not your turn

    def Manage_Dealing_Boom(self):

        game = Game.objects.get(pk=self.request.session['game_pk'])
        match = game.matchs.last()

        username = self.request.session['user_username']
        user = User.objects.get(username=username)

        # user threw boombs
        if not Logic.Check_User_Boom(game, user):
            return JsonResponse({'status': False})

        Logic.Dealing_Boom_Points(game, user)
        Stock_Card.objects.filter(game=game).delete()

        # save information about boom
        match.is_boom = True
        match.bidded_user = user
        match.save()

        # new dealing
        game.start_user = game.Get_Next_User(game.start_user)
        game.current_user = game.Get_Next_User(game.start_user)
        game.marriage_color = None
        game.save()

        Logic.Dealing_Cards(game.pk)
        return JsonResponse({'status': True})

    def Manage_Game(self):

        # not valid
        self.validate_user = True
        if not self.Check_Validate_User():
            return JsonResponse({'status': 1})

        if '__finish__' in self.request.POST:
            return self.Manage_Finish_Bidding()

        if '__win__' in self.request.POST: # for winner
            return self.Manage_Get_Bidding_Cards()

        if '__dealing__' in self.request.POST:
            return self.Manage_Dealing_Stock_Cards()

        if '__boom__' in self.request.POST:
            return self.Manage_Dealing_Boom()

        if '__add__' in self.request.POST:
            try: return self.Manage_Add_Bidding()
            except ValueError: # its not number
                return JsonResponse({'status': 3})

    @staticmethod
    def Launch(request):
        return Bidding_Manager(request, authorization=True, game_exists=True).JSON



class Throw_Card(Dynamic_Event_Manager):

    def Validate(self):

        pk = self.request.session['game_pk']
        game = Game.objects.get(pk=pk)
        stock_cards = game.Get_Stock_Card()

        if stock_cards.count() < 3:
            return True

        return False

    def Manage_Clear_Stock(self):
        game_pk = self.request.session['game_pk']
        Logic.Counting_Points(game_pk)
        return JsonResponse({'status': True})

    def Manage_Throw_Card(self):

        # variable
        color = self.request.POST['color']
        rank = self.request.POST['rank']
        card = Card.objects.get(
            color__name=color, rank__name=rank)

        # assigned cards
        username = self.request.session['user_username']
        user = User.objects.get(username=username)
        assigned = Assigned_Cards.objects.get(user=user)
        game = Game.objects.get(pk=self.request.session['game_pk'])

        # check if card maybe throw to stock
        if not Logic.Check_Throw_Card(game, card, user):
            return JsonResponse({'status': False})

        # check if call marriage now
        if Logic.Check_If_Marriage(game, card, user):
            Logic.Do_Marriage(game, card, user)

        # remove card
        assigned.cards.remove(card)

        # add card to stock
        stock_card = Stock_Card(card=card, game=game, user=user)
        if Stock_Card.objects.filter(game=game).count() == 0:
            stock_card.is_first = True

        stock_card.save()

        # change current user
        game.current_user = game.Get_Next_User()
        game.save()

        return JsonResponse({'status': True})

    def Manage_Game(self):

        if '__clear__' in self.request.POST:
            if not self.Validate():
                return self.Manage_Clear_Stock()

        self.validate_user = True
        if '__throw__' in self.request.POST:
            if self.Validate():
                if self.Check_Validate_User():
                    return self.Manage_Throw_Card()

        return JsonResponse({'error': 'not valid'})

    @staticmethod
    def Launch(request):
        return Throw_Card(request, authorization=True,
                          game_exists=True).JSON



class Get_Game_Users(Dynamic_Event_Manager):

    def Manage_Game(self):
        pk = self.request.session['game_pk']
        game = Game.objects.get(pk=pk)
        users = game.users.values('username')
        return JsonResponse({'users': list(users)})

    @staticmethod
    def Launch(request):
        return Get_Game_Users(request, authorization=True, game_exists=True).JSON


