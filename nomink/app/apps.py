from django.apps import AppConfig
from django.db.models.signals import post_migrate


class AppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app'

    def ready(self):
        from .signals import crear_grupos_y_usuarios
        post_migrate.connect(crear_grupos_y_usuarios, sender=self)
