from arbuz.models import *


class User(Abstract_Model):

    username = models.CharField(max_length=20, primary_key=True)
    password = models.CharField(max_length=75)
    online = models.BooleanField()

    def __str__(self):
        return self.username
