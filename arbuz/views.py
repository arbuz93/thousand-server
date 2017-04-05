from arbuz.base import *
from session.views import *
from abc import ABCMeta, abstractmethod


class Manager(Dynamic_Base):

    def Manage_Init(self):
        return JsonResponse({})

    def Manage_Game(self):
        return JsonResponse({})

    def Manage_Form(self):
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

    def Check_Authorization(self):

        if self.authorization:
            if self.request.session['user_login']:
                return True
            return False

        return True

    def __init__(self, request):
        Dynamic_Base.__init__(self, request)

        self.ERROR_HTML = None
        self.authorization = False



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

        if '__init__' in self.request.POST:
            return self

        # parts of pages
        if '__game__' in self.request.POST:
            return self.Manage_Game()

        # manage forms
        if '__form__' in self.request.POST:
            return self.Manage_Form()

        return self.Error_No_Event()

    def Initialize(self):

        self.Update()

        if self.request.method == 'POST':
            if self.Check():
                return self.Manage()

            return self.ERROR_HTML

        if self.request.method == 'GET':
            return HttpResponse('It is not for you')

    def __init__(self, request,
                 autostart=True,
                 authorization=False,
                 error_method=None,
                 other_value={}):

        Manager.__init__(self, request)
        Checker.__init__(self, request)
        Updater.__init__(self, request)

        self.authorization = authorization
        self.error_method = error_method
        self.other_value = other_value

        if autostart:

            try:

                self.Timer_Start()
                self.HTML = self.Initialize()
                self.Display_Status()

                if not self.HTML:
                    self.Display_Status(message='NOT HTML')

            except Exception as exception:

                self.Display_Status(message='INTERNAL')
                raise exception

    @staticmethod
    @abstractmethod
    def Launch(request):
        return Dynamic_Event_Manager(request)