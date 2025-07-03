from django.db import models
from .prestacion import Prestacion
from .paciente import Paciente


class Presupuesto(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)
    financiadora = models.CharField(max_length=100, blank=True, null=True, verbose_name="Financiadora")
    total = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Presupuesto {self.id} - {self.paciente}"

class DetallePresupuesto(models.Model):
    presupuesto = models.ForeignKey(Presupuesto, on_delete=models.CASCADE, related_name="detalles")
    prestacion = models.ForeignKey(Prestacion, on_delete=models.CASCADE)
    nombre_prestacion = models.CharField(max_length=100)
    precio_base = models.DecimalField(max_digits=10, decimal_places=2)
    porcentaje_convenio = models.IntegerField(verbose_name="Porcentaje de cobertura")
    descuento_aplicado = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Detalle {self.id} - {self.prestacion.nombre} en Presupuesto {self.presupuesto.id}"
