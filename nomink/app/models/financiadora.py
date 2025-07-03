from django.db import models
from .prestacion import Prestacion

class Financiadora(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

class ConvenioPrestaciones(models.Model):
    financiadora = models.ForeignKey(Financiadora, on_delete=models.CASCADE)
    prestacion = models.ForeignKey(Prestacion, on_delete=models.CASCADE)
    porcentaje = models.IntegerField(verbose_name="Porcentaje de Cobertura")
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField(null=True, blank=True)

    class Meta:
        verbose_name = "Cobertura de Financiadora con Prestación"
        verbose_name_plural = "Coberturas de Financiadora con Prestaciones"
        indexes = [
            models.Index(fields=["financiadora", "prestacion", "fecha_inicio"]),
            models.Index(fields=["financiadora", "prestacion", "fecha_fin"]),
        ]
