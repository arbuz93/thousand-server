from arbuz.models import *
import string, random


class User(Abstract_Model):

    unique = models.CharField(max_length=8, primary_key=True)
    username = models.CharField(max_length=20)
    password = models.CharField(max_length=75)

    @staticmethod
    def Generate_User_Unique():

        unique = ''
        permitted_chars = string.ascii_letters + \
                          string.digits

        for char_number in range(0, 8):
            unique += random.choice(permitted_chars)

        if {'unique': unique} in User.objects.values('unique'):
            return User.Generate_User_Unique()

        return unique

    def __str__(self):
        return self.username
