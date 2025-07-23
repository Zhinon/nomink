from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test

def es_convenios(user):
    return user.groups.filter(name="convenios").exists()


@login_required
@user_passes_test(es_convenios)
def convenios_view(request):
    # Próximamente: gestión de precios, descuentos y convenios
    return render(request, "convenios/index.html")
