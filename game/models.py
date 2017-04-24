from logic.models import *


class Game(Abstract_Model):

    users = models.ManyToManyField(User)
    start_user = models.ForeignKey(User, related_name='start')
    current_user = models.ForeignKey(User, related_name='current', blank=True, null=True)
    matchs = models.ManyToManyField(Match)
    is_bidding = models.BooleanField(default=True)
    is_dealing = models.BooleanField(default=False)
    marriage_color = models.ForeignKey(Color, default=None, null=True)

    def Get_Next_User(self, user=None):

        if not user:
            user = self.current_user

        # get users information
        users = list(self.users.all())
        number_of_users = self.users.count()
        number_current_user = users.index(user)

        # new current user
        number_next_user = (number_current_user + 1) % number_of_users
        return users[number_next_user]

    def Get_Stock_Card(self):

        pks = Stock_Card.objects.filter(game=self)\
            .values('card__pk')

        return Card.objects.filter(pk__in=pks)

    def __str__(self):
        return str(self.pk)



class Stock_Card(Abstract_Model):

    user = models.ForeignKey(User, blank=True, null=True)
    card = models.ForeignKey(Card)
    game = models.ForeignKey(Game)
    is_first = models.BooleanField(default=False)

    def __str__(self):
        return str(self.pk)

