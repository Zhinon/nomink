from django.db import models


class Prestacion(models.Model):
    nombre = models.CharField(max_length=100)
    codigo = models.CharField(max_length=20, unique=True, null=False)
    is_radiofarmaco = models.BooleanField(default=False, verbose_name="Es Radiofármaco?")
    is_insumo = models.BooleanField(default=False, verbose_name="Es Insumo?")

    def __str__(self):
        return f"{self.nombre} ({self.codigo})"

    class Meta:
        verbose_name = "Prestación"
        verbose_name_plural = "Prestaciones"
        ordering = ['nombre']


class PrestacionPrecio(models.Model):
    prestacion = models.ForeignKey(Prestacion, on_delete=models.CASCADE, related_name="historial_precios")
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField(null=True, blank=True)

    class Meta:
        verbose_name = "Precio historico"
        verbose_name_plural = "Historial del precio de Prestaciones"
        indexes = [
            models.Index(fields=["prestacion", "fecha_inicio"]),
            models.Index(fields=["prestacion", "fecha_fin"]),
        ]
