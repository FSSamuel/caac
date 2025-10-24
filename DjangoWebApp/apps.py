from django.apps import AppConfig


class DjangowebappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'DjangoWebApp'



class DjangoWebAppConfig(AppConfig):
    # ...
    def ready(self):
        import notifications.signals


        