from user.models import *


class Color(Abstract_Model):

    name = models.CharField(max_length=10, primary_key=True)

    def __str__(self):
        return self.name



class Rank(Abstract_Model):

    name = models.CharField(max_length=10, primary_key=True)
    points = models.IntegerField()

    def __str__(self):
        return self.name



class Card(Abstract_Model):

    color = models.ForeignKey(Color)
    rank = models.ForeignKey(Rank)

    def __str__(self):
        return self.color.name + ' ' + self.rank.name



class Assigned_Cards(Abstract_Model):

    user = models.ForeignKey(User)
    cards = models.ManyToManyField(Card)

    def __str__(self):
        return str(self.pk)



class Score(Abstract_Model):

    score = models.IntegerField()
    user = models.ForeignKey(User)

    def __str__(self):
        return str(self.score)



class Bidding(Abstract_Model):

    points = models.IntegerField()
    user = models.ForeignKey(User)

    def __str__(self):
        return self.points



class Match(Abstract_Model):

    scores = models.ManyToManyField(Score)
    biddings = models.ManyToManyField(Bidding)
    bidded_user = models.ForeignKey(User, blank=True, null=True)
    is_boom = models.BooleanField(default=False)

    def __str__(self):
        return 'match: ' + str(self.pk)
