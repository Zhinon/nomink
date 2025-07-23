from urllib import request
from django.contrib.admin import AdminSite, ModelAdmin
from django.http import HttpResponseRedirect
from django.utils.translation import gettext_lazy as _
from app.forms.prestacion_form import PrestacionForm
from app.models import Prestacion, Financiadora, PrestacionPrecio, ConvenioPrestaciones, Estudio, Servicio, CoberturaMatrix
from django.db import models
from django.contrib import admin
from django import forms
from django.utils.timezone import now
from django.utils.html import format_html
from django.db.models import OuterRef, Subquery, F, ExpressionWrapper, fields, DateField
from app.forms.estudio_form import EstudioForm
from django.urls import reverse
from django.utils.dateparse import parse_date
from datetime import date
from django.urls import path
from django.template.response import TemplateResponse
from app.admin_helpers.prestacion_precio_fecha_filter import VigenteEnFechaFilter
from django.utils.dateformat import format
from django.contrib.admin import DateFieldListFilter
from django.contrib.admin.views.main import ChangeList
from django.forms.models import modelformset_factory


class ConveniosAdminSite(AdminSite):
    site_header = "Panel de Convenios"
    site_title = "Convenios"
    index_title = "Administración de Convenios"

    def has_permission(self, request):
        return (
            request.user.is_active and
            request.user.is_authenticated and
            request.user.groups.filter(name="Convenios").exists()
        )


convenios_admin_site = ConveniosAdminSite(name='convenios_admin')

# Admin personalizado para Servicio
class ServicioAdmin(ModelAdmin):
    list_display = ["codigo", "nombre"]
    # list_editable = ["nombre"]
    search_fields = ["nombre", "codigo"]
    list_per_page = 50

# Admin personalizado para Estudio
class EstudioAdmin(ModelAdmin):
    form = EstudioForm
    list_display = ["id", "nombre", "codigo"]
    # list_editable = ["nombre"]
    search_fields = ["nombre", "codigo"]
    list_per_page = 50

# Admin personalizado para Prestacion
# Formulario para inline con fecha precargada y fecha_fin oculta
class PrestacionPrecioInlineForm(forms.ModelForm):
    class Meta:
        model = PrestacionPrecio
        fields = ['precio', 'fecha_inicio']  # ocultamos fecha_fin

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:  # solo si es nuevo
            self.fields['fecha_inicio'].initial = now().date()


# Inline admin
class PrestacionPrecioInline(admin.TabularInline):
    model = PrestacionPrecio
    form = PrestacionPrecioInlineForm
    extra = 1

    # Para ocultar fecha_fin visualmente en el inline (aunque está en el modelo)
    def get_fields(self, request, obj=None):
        return ['precio', 'fecha_inicio']  # no mostramos fecha_fin


# Admin de Prestacion
class PrestacionAdmin(admin.ModelAdmin):
    form = PrestacionForm
    list_display = ("codigo", "nombre", "is_radiofarmaco", "is_insumo", "precio_actual", "dias_desde_ultimo_precio")
    list_editable = ("nombre", "is_radiofarmaco", "is_insumo")
    search_fields = ("nombre", "codigo")

    def save_model(self, request, obj, form, change):
        nuevo_precio = form.cleaned_data.get("precio")

        # Guardamos primero la prestación
        super().save_model(request, obj, form, change)

        if nuevo_precio is not None:
            precio_vigente = PrestacionPrecio.objects.filter(
                prestacion=obj,
                fecha_fin__isnull=True
            ).order_by("-fecha_inicio").first()

            if not precio_vigente or precio_vigente.precio != nuevo_precio:
                # Cerramos el precio anterior
                if precio_vigente:
                    precio_vigente.fecha_fin = now()
                    precio_vigente.save()

                # Creamos nuevo
                PrestacionPrecio.objects.create(
                    prestacion=obj,
                    precio=nuevo_precio,
                    fecha_inicio=now()
                )

    def precio_actual(self, obj):
        vigente = obj.historial_precios.filter(fecha_fin__isnull=True).order_by('-fecha_inicio').first()
        return f"${vigente.precio:.2f}" if vigente else "—"
    precio_actual.short_description = "Precio actual"  # type: ignore

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        vigente = PrestacionPrecio.objects.filter(
            prestacion=OuterRef('pk'),
            fecha_fin__isnull=True
        ).order_by('-fecha_inicio')

        return qs.annotate(
            ultima_fecha_inicio=Subquery(vigente.values('fecha_inicio')[:1]),
            dias_sin_cambio=ExpressionWrapper(
                now().date() - F('ultima_fecha_inicio'),  # type: ignore
                output_field=fields.DurationField()
            )
        )

    def dias_desde_ultimo_precio(self, obj):
        dias = obj.dias_sin_cambio.days if obj.dias_sin_cambio is not None else None
        if dias is None:
            return "—"

        if dias > 180:
            color = "#ff4d4d"
        elif dias > 50:
            color = "#ffcc00"
        else:
            color = "#62ec82"

        return format_html(
            '<span style="background-color: {}; color: black; padding: 3px 8px; border-radius: 5px;">{} días</span>',
            color,
            dias
        )

    dias_desde_ultimo_precio.short_description = "Días desde el último cambio de precio"  # type: ignore
    dias_desde_ultimo_precio.admin_order_field = 'dias_sin_cambio'  # type: ignore


class FinanciadoraAdmin(admin.ModelAdmin):

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('coberturas/', self.admin_site.admin_view(self.coberturas_view), name="coberturas_matrix"),
        ]
        return custom_urls + urls

    def coberturas_view(self, request):
        from .models import Prestacion, Financiadora, ConvenioPrestaciones
        from django.utils.timezone import now

        prestaciones = Prestacion.objects.all()
        financiadoras = Financiadora.objects.all()
        hoy = now().date()

        if request.method == "POST":
            for key, value in request.POST.items():
                if key.startswith("input_"):
                    _, prest_id, fin_id = key.split("_")
                    prest_id = int(prest_id)
                    fin_id = int(fin_id)
                    valor = value.strip()

                    # Cierra convenio vigente si existe
                    vigente = ConvenioPrestaciones.objects.filter(
                        prestacion_id=prest_id,
                        financiadora_id=fin_id,
                        fecha_fin__isnull=True,
                    ).first()
                    if vigente and valor != str(vigente.porcentaje):
                        vigente.fecha_fin = hoy
                        vigente.save()
                        ConvenioPrestaciones.objects.create(
                            prestacion_id=prest_id,
                            financiadora_id=fin_id,
                            porcentaje=int(valor),
                            fecha_inicio=hoy,
                        )
                    elif not vigente and valor:
                        ConvenioPrestaciones.objects.create(
                            prestacion_id=prest_id,
                            financiadora_id=fin_id,
                            porcentaje=int(valor),
                            fecha_inicio=hoy,
                        )

        # Datos para render
        convenios = ConvenioPrestaciones.objects.filter(fecha_fin__isnull=True)
        cobertura_map = {}
        dias_map = {}

        hoy = now().date()
        for c in convenios:
            key = f"{c.prestacion_id}_{c.financiadora_id}"  # type: ignore
            cobertura_map[key] = c.porcentaje
            dias_map[key] = (hoy - c.fecha_inicio).days

        context = {
            **self.admin_site.each_context(request),
            "prestaciones": prestaciones,
            "financiadoras": financiadoras,
            "cobertura_map": cobertura_map,
            "dias_map": dias_map,
        }
        return TemplateResponse(request, "convenios/convenios_matrix.html", context)

class CoberturaMatrixAdmin(admin.ModelAdmin):
    def changelist_view(self, request, extra_context=None):  # type: ignore
        url = reverse('convenios_admin:coberturas_matrix')
        return HttpResponseRedirect(url)

    def has_module_permission(self, request):
        return True

    def has_view_permission(self, request, obj=None):
        return True

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class PrestacionPrecioAdmin(admin.ModelAdmin):
    change_list_template = "convenios/prestacionprecio_changelist.html"  # Custom template
    list_display = ("prestacion", "precio_formateado", "fecha_inicio_formateada", "fecha_fin_formateada")
    search_fields = ["prestacion__nombre"]

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}

        # Guardamos la fecha para mostrarla en el template
        vigente_en = request.GET.get("vigente_en")
        extra_context["vigente_en"] = vigente_en or date.today().isoformat()

        # Evitamos que Django borre el parámetro
        if "vigente_en" in request.GET:
            request.GET = request.GET.copy()
            request.GET.pop("vigente_en")


        return super().changelist_view(request, extra_context=extra_context)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        fecha_str = request.META.get("QUERY_STRING", "").split("vigente_en=")[-1].split("&")[0]

        if not fecha_str:
            return qs

        fecha = parse_date(fecha_str)
        if not fecha:
            return qs

        vigentes = {}
        for p in qs.filter(fecha_inicio__lte=fecha).order_by("prestacion_id", "-fecha_inicio"):
            if p.prestacion_id not in vigentes and (not p.fecha_fin or p.fecha_fin >= fecha):
                vigentes[p.prestacion_id] = p
        return qs.filter(id__in=[p.id for p in vigentes.values()])

    def precio_formateado(self, obj):
        return f"${obj.precio:.2f}" if obj.precio is not None else "—"
    precio_formateado.short_description = "Precio"  # type: ignore

    def fecha_inicio_formateada(self, obj):
        return obj.fecha_inicio.strftime("%d/%m/%Y") if obj.fecha_inicio else "—"
    fecha_inicio_formateada.short_description = "Fecha Inicio"  # type: ignore

    def fecha_fin_formateada(self, obj):
        return obj.fecha_fin.strftime("%d/%m/%Y") if obj.fecha_fin else "—"
    fecha_fin_formateada.short_description = "Fecha Fin"  # type: ignore

# Admin para ConvenioPrestaciones
class ConvenioPrestacionesAdmin(ModelAdmin):
    list_display = ["id", "financiadora", "prestacion"]
    search_fields = ["financiadora__nombre", "prestacion__nombre"]


# Registrar con configuraciones personalizadas
convenios_admin_site.register(Servicio, ServicioAdmin)
convenios_admin_site.register(Estudio, EstudioAdmin)
convenios_admin_site.register(Prestacion, PrestacionAdmin)
convenios_admin_site.register(Financiadora, FinanciadoraAdmin)
convenios_admin_site.register(PrestacionPrecio, PrestacionPrecioAdmin)
convenios_admin_site.register(ConvenioPrestaciones, ConvenioPrestacionesAdmin)
convenios_admin_site.register(CoberturaMatrix, CoberturaMatrixAdmin)
