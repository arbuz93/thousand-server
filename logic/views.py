from arbuz.views import *
from game.models import *


class Dealing_Cards(Dynamic_Base):

    @staticmethod
    def Get_Win_Bidding(game):
        last_match = game.matchs.last()
        max_points = last_match.biddings.all() \
            .aggregate(models.Max('points'))['points__max']

        return last_match.biddings.get(points=max_points)

    @staticmethod
    def Find_Next_User(game, match):

        next_user = game.Get_Next_User()
        if not match.biddings.filter(user=next_user, points=0):
            return next_user

        next_user = game.Get_Next_User(next_user)
        if not match.biddings.filter(user=next_user, points=0):
            return next_user

        return None

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

        bidding = Bidding(points=100, user=game.start_user)
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
        game.is_bidding = True
        game.save()

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

    @staticmethod
    def Get_All_User_Scores(game, user):
        matchs = game.matchs.all().values('scores__pk')
        scores = Score.objects.filter(user=user, pk__in=matchs)

        points = 0
        for score in scores:
            points += score.score

        return points

    @staticmethod
    def Check_User_Boom(game, user):
        booms = game.matchs.filter(
            bidded_user=user, is_boom=True)

        if booms.count() == 0:
            return True

        if booms.count() == 1:

            all_points = Dealing_Cards\
                .Get_All_User_Scores(game, user)

            if all_points >= 500:
                return True

        return False

    @staticmethod
    def Dealing_Boom_Points(game, user):

        other_users_scores = game.matchs.last() \
            .scores.exclude(user=user)

        # diving points
        first_user = other_users_scores[0]
        first_user.score = 60
        first_user.save()

        second_user = other_users_scores[1]
        second_user.score = 60
        second_user.save()

        # boom user
        boom_user = game.matchs.last() \
            .scores.get(user=user)

        boom_user.score = 0
        boom_user.save()



class Point_Counter(Dynamic_Base):

    @staticmethod
    def Marriage_Points(color):

        colors = {
            'Heart':    100,
            'Diamond':  80,
            'Clover':   60,
            'Spades':   40
        }

        return  colors[color.name]

    @staticmethod
    def Count_User_Max_Points(user, game):

        # the winner bidding have stock card also
        next_user = Logic.Find_Next_User(game, game.matchs.last())
        if not next_user:

            cards = Card.objects.filter(
                Q(pk__in=Assigned_Cards.objects.get(user=user).cards.all()) |
                Q(pk__in=Stock_Card.objects.all().values('card'))
            )

        else: # no one win bidding then have only self cards

            cards = Card.objects.filter(
                pk__in=Assigned_Cards.objects.get(user=user).cards.all()
            )

        kings = cards.filter(rank__name='King')
        points = 120

        for king in kings:
            if cards.filter(pk=king.pk+1):
                points += Point_Counter.Marriage_Points(king.color)

        return points

    @staticmethod
    def Do_Marriage(game, card, user):

        game.marriage_color = card.color
        game.save()

        match = game.matchs.last()
        score = match.scores.get(user=user)
        score.score += Point_Counter.Marriage_Points(card.color)
        score.save()

    @staticmethod
    def Check_If_Marriage(game, card, user):

        user_cards = Assigned_Cards.objects.get(user=user)
        first_card = Stock_Card.objects.filter(
            game=game, is_first=True)

        # first card exists
        if first_card:
            return False

        # check throw card and find marriage
        if card.rank.name == 'King':
            if user_cards.cards.filter(color=card.color, rank__name='Queen'):
                return True

        if card.rank.name == 'Queen':
            if user_cards.cards.filter(color=card.color, rank__name='King'):
                return True

        # not marriage
        return False

    @staticmethod
    def Get_Greater_Card_In_Color(card_1, card_2, card_3=None):

        # compare two cards
        if card_1.card.rank.points > card_2.card.rank.points:
            max_card = card_1

        else: max_card = card_2

        # no third card
        if not card_3:
            return max_card

        # compare max with third
        if card_3.card.rank.points > max_card.card.rank.points:
            return card_3

        else: return max_card

    @staticmethod
    def Get_Biggest_Card_In_Stock(game):

        # check if any cards are in stock
        if not Stock_Card.objects.filter(game=game, is_first=True):
            return None

        stock = Stock_Card.objects.filter(game=game)
        base_color = stock.get(is_first=True).card.color
        marriage_color = game.marriage_color

        # stock contain card with marriage color
        cards_marriage_color = stock.filter(card__color=marriage_color)
        if cards_marriage_color:

            # one card have marriage color
            if cards_marriage_color.count() == 1:
                return cards_marriage_color[0]

            # two card have marriage color
            if cards_marriage_color.count() == 2:
                return Point_Counter.Get_Greater_Card_In_Color(
                    cards_marriage_color[0], cards_marriage_color[1])

            # if three card have marriage color
            # than the color is base color

        # stock doesn't contain card with marriage color
        # and contain base color cards
        cards_base_color = stock.filter(card__color=base_color)
        if cards_base_color:

            # one card have base color
            if cards_base_color.count() == 1:
                return cards_base_color[0]

            # two card have marriage color
            if cards_base_color.count() == 2:
                return Point_Counter.Get_Greater_Card_In_Color(
                    cards_base_color[0], cards_base_color[1])

            # three card have marriage color
            if cards_base_color.count() == 3:
                return Point_Counter.Get_Greater_Card_In_Color(
                    cards_base_color[0], cards_base_color[1],
                    cards_base_color[2])

    @staticmethod
    def Check_Throw_Card(game, card, user):

        user_cards = Assigned_Cards.objects.get(user=user)
        biggest_card = Point_Counter.Get_Biggest_Card_In_Stock(game)

        # stock is empty
        if not biggest_card:
            return True

        # color is equal and throw card is greater
        if biggest_card.card.color == card.color:
            if card.rank.points > biggest_card.card.rank.points:
                return True

        # user have cards greater than biggest card in stock
        color_cards = user_cards.cards.filter(color=biggest_card.card.color)
        if color_cards.filter(rank__points__gt=biggest_card.card.rank.points):
            return False

        # color is not marriage color and user have marriage card
        if not color_cards:
            if biggest_card.card.color != game.marriage_color:
                if card.color != game.marriage_color:
                    if user_cards.cards.filter(color=game.marriage_color):
                        return False

        # card have another color but user have the color
        if biggest_card.card.color != card.color:
            if color_cards.count():
                return False

        # good
        return True

    @staticmethod
    def Save_Points(winner, stock, match):

        score = match.scores.get(user=winner.user)
        for card in stock:
            score.score += card.card.rank.points

        score.save()

    @staticmethod
    def Save_Match_Points(game):

        # check points winner bidded user
        bidded_user = Logic.Get_Win_Bidding(game)
        bidded_user_score = game.matchs.last()\
            .scores.get(user=bidded_user.user)

        # bidded user lose
        if bidded_user_score.score < bidded_user.points:
            bidded_user_score.score = -bidded_user.points

        else: bidded_user_score.score = bidded_user.points
        bidded_user_score.save()

        # round scores
        scores = game.matchs.last().scores.all()
        for score in scores:

            # user have 800 points and is not bidded user
            if Logic.Get_All_User_Scores(game, score.user) >= 800:
                if bidded_user.user != score.user:
                    score.score = 0

            else: score.score = round(score.score, -1)
            score.save()

    @staticmethod
    def Check_If_Game_Is_Over(game):

        for user in game.users.all():
            if Logic.Get_All_User_Scores(game, user) >= 1000:
                game.is_over = True # game over
                game.winner = user
                game.save()

    @staticmethod
    def Check_If_Match_Is_Over(winner, game):

        assigned = Assigned_Cards.objects.get(user=winner.user)
        if assigned.cards.count() == 0: # match is over

            # check over points
            Point_Counter.Save_Match_Points(game)

            # new dealing
            game.start_user = game.Get_Next_User(game.start_user)
            game.current_user = game.Get_Next_User(game.start_user)
            game.marriage_color = None
            game.save()

            Logic.Check_If_Game_Is_Over(game)
            Logic.Dealing_Cards(game.pk)

    @staticmethod
    def Get_Stock_Winner(stock, first_card, game):

        # stock contain cards with marriage color
        if stock.filter(card__color=game.marriage_color):

            stock = stock.filter(card__color=game.marriage_color)
            max_points = stock.aggregate(models.Max('card__rank__points'))
            max_points = max_points['card__rank__points__max']
            winner = stock.filter(card__rank__points=max_points)

        # stock not contain
        else:

            # search winner in first card color
            stock = stock.filter(card__color=first_card.card.color)
            max_points = stock.aggregate(models.Max('card__rank__points'))
            max_points = max_points['card__rank__points__max']
            winner = stock.filter(card__rank__points=max_points)

        # if all cards is another colors
        if not winner:
            return first_card

        else: return winner[0]

    @staticmethod
    def Counting_Points(game_pk):

        game = Game.objects.get(pk=game_pk)
        stock = Stock_Card.objects.filter(game=game)
        first_card = stock.filter(is_first=True)

        # if stock is empty
        if not first_card:
            return

        else: first_card = first_card[0]

        # search winner
        winner = Point_Counter.Get_Stock_Winner(
            stock, first_card, game)

        # winner is current user
        game.current_user = winner.user
        game.save()

        # save points for winner
        Point_Counter.Save_Points(winner, stock, game.matchs.last())
        stock.delete()

        # check if match is over
        Point_Counter.Check_If_Match_Is_Over(winner, game)



class Logic(Dealing_Cards, Point_Counter):
    pass
