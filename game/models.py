from logic.models import *


class Game(Abstract_Model):

    users = models.ManyToManyField(User)
    start_user = models.ForeignKey(User, related_name='start')
    current_user = models.ForeignKey(User, related_name='current')
    matchs = models.ManyToManyField(Match)

    def __str__(self):
        return str(self.pk)



class Chat(Abstract_Model):

    message = models.CharField(max_length=1000)
    date = models.DateTimeField(auto_now_add=True, blank=True)
    game = models.ForeignKey(Game)
    user = models.ForeignKey(User)

    def __str__(self):
        return self.message
