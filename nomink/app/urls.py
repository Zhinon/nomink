"""
URL configuration for app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.contrib.auth.views import LogoutView
from app.views import auth_views, turnos_views, prestacion_autocomplete_views
from app.convenios_admin import convenios_admin_site


urlpatterns = [
    path('admin/', admin.site.urls),
    path("convenios/", convenios_admin_site.urls),
    path("login/", auth_views.custom_login, name="login"),
    path("logout/", LogoutView.as_view(next_page='login'), name="logout"),
    path("dashboard/", auth_views.dashboard, name="dashboard"),
    path("presupuestos/", turnos_views.presupuestos_view, name="presupuestos"),
    path('prestacion-autocomplete/', prestacion_autocomplete_views.PrestacionAutocomplete.as_view(), name='prestacion-autocomplete'),

    # path("convenios/", views.convenios_view, name="convenios"),
]
