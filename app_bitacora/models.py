from django.contrib.auth.models import AbstractUser
from django.db import models

class Usuario(AbstractUser):
    # El nombre de usuario y la contraseña la maneja el AbstractUser
    # Sobrescribí el campo email que viene por defecto con AbstractUser
    email = models.EmailField(unique=True, blank=False, null=False)

    # Otros campos personalizados
    pais = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.username

class Coleccion(models.Model):
    nombre_coleccion = models.CharField(max_length=80)
    detalle_coleccion = models.CharField(max_length=400)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE) # Relación uno a muchos

    def __str__(self):
        return self.nombre_coleccion

class Entrada(models.Model):
    detalle_entrada = models.CharField(max_length=800)
    # video_entrada = ...
    fecha_entrada = models.DateTimeField("date published")

    OPCIONES_TIPO_ENTRADA = {
        "privada": "Entrada Privada",
        "publica": "Entrada Publica",
    }

    tipo_entrada = models.CharField(max_length=20, choices=OPCIONES_TIPO_ENTRADA)
    #acá estoy diciendo que la entrada tiene como foreign key a usuario
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE) # Relación uno a muchos
    imagen = models.ImageField(
        upload_to='imagenes/',  # Carpeta donde se guardarán las imágenes
        null=True, # El campo acepta nulos en la BD
        blank=True # El campo es opcional al momento de completar el formulario
    )
    colecciones = models.ManyToManyField(Coleccion, related_name='entradas', blank=True)  # Relación muchos a muchos
    def __str__(self):
        return self.detalle_entrada