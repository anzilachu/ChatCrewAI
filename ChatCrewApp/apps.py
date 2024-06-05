from django.apps import AppConfig


class ChatcrewappConfig(AppConfig):
    name = 'ChatCrewApp'

    def ready(self):
        import ChatCrewApp.signals