from django.db import models
from .financiadora import Financiadora


class Paciente(models.Model):
    nombre = models.CharField(max_length=100)
    dni = models.CharField(max_length=20)
    financiadora = models.ForeignKey(Financiadora, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.nombre} ({self.dni})"
