from django.db import models


class Base_Model:

    def Set_Variables(self):
        pass

    def __init__(self):
        self.Set_Variables()



class Abstract_Model(Base_Model, models.Model):

    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        models.Model.__init__(self, *args, **kwargs)
        Base_Model.__init__(self)

