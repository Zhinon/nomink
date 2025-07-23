from dal import autocomplete
from django import forms
from app.models import Estudio

class EstudioForm(forms.ModelForm):
    class Meta:
        model = Estudio
        fields = "__all__"
        widgets = {
            'prestaciones': autocomplete.ModelSelect2Multiple(
                url='prestacion-autocomplete'
            )
        }
