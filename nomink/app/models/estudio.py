from django.db import models
from .servicio import Servicio


class Estudio(models.Model):
    nombre = models.CharField(max_length=100)
    codigo = models.CharField(max_length=20, unique=True, null=False)
    prestaciones = models.ManyToManyField('Prestacion', blank=True)
    servicio = models.ForeignKey(Servicio, null=False, on_delete=models.DO_NOTHING)

    def __str__(self):
        return f"{self.nombre} ({self.codigo})"

    class Meta:
        verbose_name = "Estudio"
        verbose_name_plural = "Estudios"
        ordering = ['nombre']
