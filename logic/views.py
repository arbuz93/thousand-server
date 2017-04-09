from arbuz.views import *
from logic.models import *
from game.models import *


class Logic(Dynamic_Base):

    @staticmethod
    def Clear_Assigned_Cards(users):

        for user in users:
            Assigned_Cards.objects\
                .filter(user=user).delete()

    @staticmethod
    def Rand_Cards(user, cards):

        user_cards = Assigned_Cards(user=user)
        user_cards.save()

        for k in range(0, 7):
            card = random.choice(cards)
            cards.remove(card)

            user_cards.cards.add(
                Card.objects.get(pk=card))

    @staticmethod
    def Create_Match(game, cards, users):

        bidding = Bidding(points=100, user=users[0])
        bidding.save()

        match = Match(game=game, bidding=bidding)
        match.save()

        # stock
        for card in cards:
            match.stock.add(Card.objects.get(pk=card))

        # scores
        for user in users:
            score = Score(score=0, user=user)
            score.save()
            match.scores.add(score)

        # adding first match to game
        game.matchs.add(match)

    @staticmethod
    def Dealing_Cards(game_pk):

        game = Game.objects.get(pk=game_pk)
        users = game.users.all()
        cards = list(range(1, 25))

        Logic.Clear_Assigned_Cards(users)
        Logic.Rand_Cards(users[0], cards)
        Logic.Rand_Cards(users[1], cards)
        Logic.Rand_Cards(users[2], cards)

        Logic.Create_Match(game, cards, users)
