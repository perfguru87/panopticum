from django.apps import AppConfig


class PanopticumConfig(AppConfig):
    name = 'panopticum'

    def ready(self):
        import panopticum.signals  # init signals
