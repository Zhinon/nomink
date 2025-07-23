from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test

def es_turnos(user):
    return user.groups.filter(name="turnos").exists()


@login_required
# @user_passes_test(es_turnos)
def presupuestos_view(request):
    # Próximamente: lógica para crear presupuestos
    return render(request, "turnos/presupuestos.html")
