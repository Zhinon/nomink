from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth.views import LogoutView


def custom_login(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("dashboard")
        else:
            return render(request, "login.html", {"error": "Credenciales inválidas"})
    return render(request, "login.html")


@login_required
def dashboard(request):
    user = request.user
    if user.is_superuser:
        return redirect("/admin/")
    elif user.groups.filter(name="turnos").exists():
        return redirect("/presupuestos/")
    elif user.groups.filter(name="Convenios").exists():
        return redirect("/convenios/")
    else:
        return render(request, "dashboard.html", {"error": "No tenés un rol asignado"})
