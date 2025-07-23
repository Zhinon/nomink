from django.contrib.auth.models import Group, Permission, User
from django.contrib.contenttypes.models import ContentType
from django.apps import apps
from django.db import IntegrityError

def crear_grupos_y_usuarios(sender, **kwargs):
    try:
        modelos = {
            "Servicio": apps.get_model("app", "Servicio"),
            "Estudio": apps.get_model("app", "Estudio"),
            "Prestacion": apps.get_model("app", "Prestacion"),
            "PrestacionPrecio": apps.get_model("app", "PrestacionPrecio"),
            "Financiadora": apps.get_model("app", "Financiadora"),
            "ConvenioPrestaciones": apps.get_model("app", "ConvenioPrestaciones"),
            "Paciente": apps.get_model("app", "Paciente"),
            "Presupuesto": apps.get_model("app", "Presupuesto"),
            "DetallePresupuesto": apps.get_model("app", "DetallePresupuesto"),
        }

        grupo_convenio, _ = Group.objects.get_or_create(name="Convenios")
        grupo_turnos, _ = Group.objects.get_or_create(name="Turnos")

        # Convenio: CRUD en modelos administrativos
        for model in ["Servicio", "Estudio", "Prestacion", "PrestacionPrecio", "Financiadora", "ConvenioPrestaciones"]:
            ct = ContentType.objects.get_for_model(modelos[model])
            for codename in ["add", "change", "delete"]:
                permiso = Permission.objects.get(content_type=ct, codename=f"{codename}_{model.lower()}")
                grupo_convenio.permissions.add(permiso)

        # Turnos: lectura general, alta de pacientes y presupuestos
        for model in ["Servicio", "Estudio", "Prestacion", "PrestacionPrecio", "Financiadora", "ConvenioPrestaciones"]:
            ct = ContentType.objects.get_for_model(modelos[model])
            permiso = Permission.objects.get(content_type=ct, codename=f"view_{model.lower()}")
            grupo_turnos.permissions.add(permiso)

        for model in ["Paciente"]:
            ct = ContentType.objects.get_for_model(modelos[model])
            for codename in ["add", "change"]:
                permiso = Permission.objects.get(content_type=ct, codename=f"{codename}_{model.lower()}")
                grupo_turnos.permissions.add(permiso)

        for model in ["Presupuesto", "DetallePresupuesto"]:
            ct = ContentType.objects.get_for_model(modelos[model])
            permiso = Permission.objects.get(content_type=ct, codename=f"add_{model.lower()}")
            grupo_turnos.permissions.add(permiso)

        # Usuarios
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser("admin", "admin@example.com", "123")

        if not User.objects.filter(username="convenios").exists():
            u = User.objects.create_user("convenios", "convenios@example.com", "123")
            u.groups.add(grupo_convenio)
            u.is_staff = True
            u.save()

        if not User.objects.filter(username="turnos").exists():
            u = User.objects.create_user("turnos", "turnos@example.com", "123")
            u.groups.add(grupo_turnos)

    except (Permission.DoesNotExist, ContentType.DoesNotExist, IntegrityError):
        # Posiblemente aún no están todos los modelos cargados
        pass
