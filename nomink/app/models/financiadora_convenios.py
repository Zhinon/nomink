from django.db import models

class CoberturaMatrix(models.Model):
    nombre = models.CharField(max_length=20, default="test")

    class Meta:
        verbose_name = "Matriz de Coberturas"
        verbose_name_plural = "Matriz de Coberturas"
        app_label = "app"
        managed = False
