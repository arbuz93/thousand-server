from user.models import *


class Game(Abstract_Model):

    users = models.ManyToManyField(User)

    def __str__(self):
        return str(self.pk)



class Score(Abstract_Model):

    score = models.IntegerField()
    game = models.ForeignKey(Game)
    user = models.ForeignKey(User)

    def __str__(self):
        return self.user



class Chat(Abstract_Model):

    message = models.CharField(max_length=1000)
    date = models.DateTimeField(auto_now_add=True, blank=True)
    game = models.ForeignKey(Game)
    user = models.ForeignKey(User)

    def __str__(self):
        return self.message
