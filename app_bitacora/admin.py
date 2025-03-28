from django.contrib import admin
from .models import Usuario, Entrada, Coleccion

# Registrar los modelos
admin.site.register(Usuario)
admin.site.register(Entrada)
admin.site.register(Coleccion)
