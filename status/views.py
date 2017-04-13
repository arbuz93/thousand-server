from game.views import *


class Check_Status_Game(Dynamic_Event_Manager):

    def Join_To_Game(self):
        username = self.request.session['user_username']
        self.reply['join'] = False

        if Game.objects.filter(users__username=username):
            self.request.session['game_pk'] = Game.objects.filter(
                users__username=username)[0].pk

            self.reply['join'] = True

    def Create_Variables(self):

        username = self.request.session['user_username']

        self.variable['game_pk'] = self.request.session['game_pk']
        self.variable['game'] = Game.objects.get(pk=self.variable['game_pk'])
        self.variable['match'] = self.variable['game'].matchs.last()
        self.variable['user'] = User.objects.get(username=username)

    def Status_Chat_Messages(self):
        messages = Chat_Manager.Get_Messages(
            self.variable['game_pk'])

        self.reply['messages'] = messages

    def Status_Assigned_Cards(self):
        cards = Assigned_Cards.objects\
            .filter(user=self.variable['user'])\
            .values('cards__color__name', 'cards__rank__name')

        self.reply['cards'] = list(cards)

    def Status_Stock(self):

        game = self.variable['game']
        stock = game.Get_Stock_Card()\
            .values('color__name', 'rank__name')

        if game.is_bidding:
            return

        self.reply['stock'] = list(stock)

    def Status_Bidding(self):
        game = self.variable['game']
        self.reply['is_bidding'] = game.is_bidding

        if game.is_bidding:

            self.reply['current_user'] = \
                game.current_user.username

            self.reply['biddings'] = \
                Bidding_Manager.Get_Biddings(game)

        if game.is_dealing:

            win_bidding = Bidding_Manager.Get_Win_Bidding(game)
            self.reply['win_bidding'] = {
                'user':     win_bidding.user.username,
                'points':   win_bidding.points
            }

    def Status_User(self):

        self.reply['current_user'] = \
            self.variable['game'].current_user.username

        self.reply['users_status'] = \
            list(self.variable['match'].scores.all()\
                .values('user__username', 'score'))

    def Manage_Game(self):

        self.Create_Variables()
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

