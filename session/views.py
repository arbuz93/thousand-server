from inspect import getmembers, ismethod


class Session_Controller:

    def Check_Session_Arbuz(self):

        if 'arbuz_app' not in self.request.session:
            self.request.session['arbuz_app'] = ''

    def Check_Session_User(self):

        if 'user_login' not in self.request.session:
            self.request.session['user_login'] = False

        if 'user_username' not in self.request.session:
            self.request.session['user_username'] = ''

    def Check_Session_Game(self):

        if 'game_pk' not in self.request.session:
            self.request.session['game_pk'] = None

    def Check_Session(self):

        methods = getmembers(self, predicate=ismethod)
        methods = [method[0] for method in methods]

        for method in methods:
            if 'Check_Session_' in method:
                getattr(Session_Controller, method)(self)


    def __init__(self, request):
        self.request = request
        self.Check_Session()



def Check_Session(request):
    Session_Controller(request)