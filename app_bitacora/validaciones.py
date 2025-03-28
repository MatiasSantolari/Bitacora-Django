from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django import forms
from django.utils import timezone

from .models import Usuario

def validar_email(email):
    try:
        validate_email(email)
    except ValidationError:
        raise forms.ValidationError("Este email no es válido.")
    if Usuario.objects.filter(email=email).exists():
        raise forms.ValidationError("Este email ya está ocupado por otra cuenta en el sistema.")

def validar_fecha_no_futura(fecha):
    if fecha > timezone.now() or fecha is None:
        raise forms.ValidationError("La fecha no puede estar en el futuro.")

def validar_username(username):
    if Usuario.objects.filter(username=username).exists():
            raise forms.ValidationError("Este nombre de usuario ya está ocupado.")

def validar_password(password, repeated_password):
    if password != repeated_password:
        raise forms.ValidationError("Las contraseñas no coinciden.")
    if len(password) < 8:
        raise forms.ValidationError("La contraseña debe tener al menos 8 caracteres.")

def validar_campo_no_repetido(campo, lista_campo=None):
    '''
        Esta validacion sirve para controlar casos como el siguiente:
        para un mismo usuario, no puede tener 2 colecciones con el mismo nombre.
            en este caso:
                -campo = un nombre para una coleccion
                -lista_campo = lista con todos los nombres de las colecciones del usuario autenticado
        ... y casos similares que puedan surgir en el futuro.
    '''
    if lista_campo is None or not isinstance(lista_campo, list):
        raise ValueError("La lista de campos proporcionada no es válida.")
    if campo in lista_campo:
        raise forms.ValidationError("Ya estás usando este nombre para otro registro, intenta con otro.")
