from arbuz.views import *
from game.models import *


class Dealing_Cards(Dynamic_Base):

    @staticmethod
    def Clear_Assigned_Cards(users):

        for user in users:
            Assigned_Cards.objects \
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

        match = Match()
        match.save()

        # stock
        for card in cards:

            Stock_Card(
                card=Card.objects.get(pk=card),
                game=game
            ).save()

        # scores
        for user in users:
            score = Score(score=0, user=user)
            score.save()
            match.scores.add(score)

        # adding first match to game
        match.biddings.add(bidding)
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



class Point_Counter(Dynamic_Base):

    @staticmethod
    def Check_Adding_Stock_Card(game, card, user):

        user_cards = Assigned_Cards.objects.get(user=user)
        first_card = Stock_Card.objects.filter(
            game=game, is_first=True)

        # first card not exists
        if not first_card:
            return True

        # get first card
        first_card = first_card[0].card

        # user have card in first card color
        if card.color != first_card.color:

            user_cards_filter = user_cards.cards.filter(
                color=first_card.color
            )

            if user_cards_filter:
                return False

        # user have card in first card color
        if card.color == first_card.color:

            user_cards_filter = user_cards.cards.filter(
                color=first_card.color,
                rank__points__gt=first_card.rank.points
            )

            # user have not greater card
            if not user_cards_filter:
                return True

            # user have one or more greater card
            # if throw card exists there
            if user_cards_filter.filter(pk=card.pk):
                return True

            # user throw too small card
            else: return False

        # good
        return True

    @staticmethod
    def Save_Points(winner, stock, match):

        score = match.scores.get(user=winner.user)
        for card in stock:
            score.score += card.card.rank.points

        score.save()

    @staticmethod
    def Counting_Points(game_pk):

        game = Game.objects.get(pk=game_pk)
        stock = Stock_Card.objects.filter(game=game)
        first_card = stock.get(is_first=True)

        print(first_card)

        # search winner in first card color
        max_points = stock.aggregate(models.Max('card__rank__points'))
        max_points = max_points['card__rank__points__max']
        winner = stock.get(card__rank__points=max_points,
                           card__color=first_card.card.color)

        # winner is current user
        game.current_user = winner.user
        game.save()

        # save points for winner
        Point_Counter.Save_Points(winner, stock, game.matchs.last())
        stock.delete()



class Logic(Dealing_Cards, Point_Counter):
    pass
