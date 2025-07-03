from django.contrib import admin
from .models import (
    Financiadora, ConvenioPrestaciones,
    Prestacion, PrestacionPrecio,
    Paciente, Presupuesto, DetallePresupuesto, Servicio,
    Estudio,
)
admin.site.register(Financiadora)
admin.site.register(ConvenioPrestaciones)
admin.site.register(Prestacion)
admin.site.register(PrestacionPrecio)
admin.site.register(Paciente)
admin.site.register(Presupuesto)
admin.site.register(DetallePresupuesto)
admin.site.register(Servicio)
admin.site.register(Estudio)
