from django.apps import AppConfig


class ApiConfig(AppConfig):
    name = 'api'
    verbose_name = 'market api'

    def ready(self):
        print("import signals")
        import cpchain.market.api.signals
