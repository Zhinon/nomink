from django import forms
from app.models import Prestacion

class PrestacionForm(forms.ModelForm):
    precio = forms.DecimalField(
        label="Precio actual",
        required=True,
        min_value=0,
        decimal_places=2
    )

    class Meta:
        model = Prestacion
        fields = ["nombre", "codigo", "is_radiofarmaco", "is_insumo"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Si es edición y hay un precio vigente, precargar
        if self.instance.pk:
            vigente = self.instance.historial_precios.filter(fecha_fin__isnull=True).order_by('-fecha_inicio').first()
            if vigente:
                self.fields["precio"].initial = vigente.precio
