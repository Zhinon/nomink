from dal import autocomplete
from app.models import Prestacion

class PrestacionAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Prestacion.objects.none()

        qs = Prestacion.objects.all()

        if self.q:
            qs = qs.filter(nombre__icontains=self.q)

        return qs
