from arbuz.base import *
from session.views import *
from game.models import *

from django.middleware import csrf
from abc import ABCMeta, abstractmethod


class Manager(Dynamic_Base):

    def Manage_Init(self):
        Check_Session(self.request)
        data = {'csrfmiddlewaretoken': csrf.get_token(self.request)}
        return JsonResponse(data)

    def Manage_Game(self):
        return JsonResponse({})

    def Clear_Session(self, key_contain=''):
        Dynamic_Base.Clear_Session(self, key_contain)
        Check_Session(self.request)

    def Index_Clear_Session(self):
        Check_Session(self.request)

    def __init__(self, request):
        Dynamic_Base.__init__(self, request)



class Checker(Dynamic_Base):

    def Error_No_Event(self):
        return JsonResponse({'error': 'authorization'})

    def Error_Authorization(self):
        return JsonResponse({'error': 'authorization'})

    def Error_Game_Exists(self):
        return JsonResponse({'error': 'game_exists'})

    def Error_Validate_User(self):
        return JsonResponse({'error': 'validate_user'})

    def Check_Authorization(self):

        if self.authorization:
            return self.request.session['user_login']

        return True

    def Check_Game_Exists(self):

        if self.game_exists:
            if self.request.session['game_pk']:
                return True

            return False
        return True

    def Check_Validate_User(self):

        if self.validate_user:
            user = User.objects.get(username=self.request.session['user_username'])
            game = Game.objects.get(pk=self.request.session['game_pk'])

            # only current user can bidding now
            if not user == game.current_user:
                return False

            return True
        return True

    def __init__(self, request):
        Dynamic_Base.__init__(self, request)

        self.ERROR_HTML = None
        self.authorization = False
        self.validate_user = False
        self.game_exists = False



class Updater(Dynamic_Base):

    def Update_App_Name(self):
        self.request.session['arbuz_app'] = self.app_name

    def __init__(self, request):
        Dynamic_Base.__init__(self, request)



class Dynamic_Event_Manager(Manager, Checker, Updater, metaclass=ABCMeta):

    def Check(self):

        if self.error_method:
            self.ERROR_HTML = self.Error()
            return False

        methods = getmembers(Checker(self.request), predicate=ismethod)
        methods = [method[0] for method in methods]

        # call all of methods Check_*
        for method in methods:
            if 'Check_' in method:

                # Check_* returned False
                if not getattr(Dynamic_Event_Manager, method)(self):

                    # render error HTML
                    method = method.replace('Check', 'Error')
                    self.ERROR_HTML = getattr(Dynamic_Event_Manager, method)(self)

                    return False

        return True

    def Update(self):

        methods = getmembers(Updater(self.request), predicate=ismethod)
        methods = [method[0] for method in methods]

        for method in methods:
            if 'Update_' in method:
                getattr(Dynamic_Event_Manager, method)(self)

    def Error(self):
        return getattr(Dynamic_Event_Manager, self.error_method)(self)

    def Manage(self):
        return self.Manage_Game()

    def Initialize(self):

        self.Update()

        if self.request.method == 'POST':
            if self.Check():
                return self.Manage()

            return self.ERROR_HTML

        if self.request.method == 'GET':
            return self.Manage_Init()

    def __init__(self, request,
                 autostart=True,
                 authorization=False,
                 validate_user=False,
                 game_exists=False,
                 error_method=None,
                 other_value={}):

        Manager.__init__(self, request)
        Checker.__init__(self, request)
        Updater.__init__(self, request)

        self.authorization = authorization
        self.validate_user = validate_user
        self.game_exists = game_exists
        self.error_method = error_method
        self.other_value = other_value
        self.reply = {}
        self.variable = {}

        if autostart:

            try:

                self.Timer_Start()
                self.JSON = self.Initialize()
                self.Display_Status()

                if not self.JSON:
                    self.Display_Status(message='NOT REPLY')

            except Exception as exception:

                self.Display_Status(message='INTERNAL')
                raise exception

    @staticmethod
    @abstractmethod
    def Launch(request):
        return Dynamic_Event_Manager(request).JSON