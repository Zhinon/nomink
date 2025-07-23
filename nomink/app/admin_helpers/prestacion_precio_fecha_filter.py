from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from datetime import datetime
from django.db import models


class VigenteEnFechaFilter(admin.SimpleListFilter):
    title = 'vigente en fecha'
    parameter_name = 'vigente_fecha'

    def lookups(self, request, model_admin):
        return []  # no usamos opciones predeterminadas

    def queryset(self, request, queryset):
        fecha_str = request.GET.get(self.parameter_name)
        if fecha_str:
            try:
                fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
                return queryset.filter(
                    fecha_inicio__lte=fecha,
                ).filter(
                    models.Q(fecha_fin__gte=fecha) | models.Q(fecha_fin__isnull=True)
                )
            except ValueError:
                pass  # Fecha inválida
        return queryset

    def choices(self, changelist):
        # reemplazamos el select por un input date
        yield {
            'selected': False,
            'query_string': '',
            'display': '🗓️ Elegir fecha en el buscador',
        }
