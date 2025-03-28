from django import forms
from django.contrib.auth.decorators import login_required

from .models import Entrada, Usuario, Coleccion

class LoginForm(forms.Form):
    nombre = forms.CharField(label="Nombre de usuario", max_length=100)
    password = forms.CharField(label="Contraseña", max_length=100, widget=forms.PasswordInput)

#para este formulario uso ModelForm porque tengo un modelo previo, entonces el form se adapta a dicho modelo
class EntradaForm(forms.ModelForm):
    class Meta:
        model = Entrada
        fields = ['detalle_entrada', 'fecha_entrada', 'tipo_entrada','imagen']
        widgets = {
            'detalle_entrada': forms.Textarea(attrs={
                'placeholder': 'Escribe el detalle de tu entrada...',
                'rows': 5,
                'cols': 50,
                'class': 'form-control',
            }),
            'fecha_entrada': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-control',
            }),
            'tipo_entrada': forms.Select(attrs={
                'class': 'form-select',
            }),
            'imagen': forms.ClearableFileInput(attrs={
                'class': 'form-control',
            }),
        }
        labels = {
            'detalle_entrada': 'Detalle de la entrada',
            'tipo_entrada': 'Tipo de entrada',
            'fecha_entrada': 'Fecha de lo sucedido',
            'imagen': 'Subir una imagen (opcional)'
        }

class RegistrarUsuarioForm(forms.ModelForm):
    repeated_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Repite tu contraseña...',
            'class': 'form-control',
        }),
        label="Repetir contraseña",
        required=True,
    )
    class Meta:
        model = Usuario
        fields = ['username', 'email', 'password', 'pais']
        widgets = {
            'username': forms.TextInput(attrs={
                'placeholder': 'Escribe tu nombre de usuario...',
                'class': 'form-control',
            }),
            'email': forms.EmailInput(attrs={
                'placeholder': 'Escribe tu cuenta de email...',
                'class': 'form-control',
            }),
            'pais': forms.TextInput(attrs={
                'placeholder': 'Escribe tu país de origen...',
                'class': 'form-control',
            }),
            'password': forms.PasswordInput(attrs={
                'placeholder': 'Escribe tu contraseña...',
                'class': 'form-control',
            })
        }
        labels = {
            'username': 'Nombre de usuario',
            'email': 'Email',
            'password': 'Contraseña',
            'pais': 'País de origen'
        }

class ColeccionForm(forms.ModelForm):
    class Meta:
        model = Coleccion
        fields = ['nombre_coleccion','detalle_coleccion']
        widgets = {
            'nombre_coleccion': forms.TextInput(attrs={
                'placeholder': 'Ingrese nombre de la coleccion...',
                'class': 'form-control',
            }),
            'detalle_coleccion': forms.Textarea(attrs={
                'placeholder': 'Ingrese detalle de la coleccion',
                'rows': 5,
                'cols': 50,
                'class': 'form-control',
            })
        }
        labels = {
            'nombre_coleccion':'Nombre de la coleccion',
            'detalle_coleccion': 'Detalle de la coleccion'
        }

class FiltrosEntradaForm(forms.Form):
    # Dejo vacia la lista de choices porque las voy a rellenar dinamicamente con el constructor __init__
    coleccion = forms.ChoiceField(choices=[], required=False, label="Filtrar por colección")
    tipo_entrada = forms.ChoiceField(
        choices=[
            ("", "Todas"),
            ("privada", "Privadas"),
            ("publica", "Públicas")
        ],
        widget=forms.RadioSelect,
        required=False,
        label="Tipo de Entrada"
    )
    busqueda_x_detalle_entrada = forms.CharField(label="Buscar entrada",
                                                 required=False,
                                                 widget=forms.TextInput(attrs={"placeholder": "Ingrese texto para buscar..."}))

    def __init__(self, *args, usuario=None, **kwargs):
        super().__init__(*args, **kwargs)
        if usuario:
            colecciones_usuario = Coleccion.objects.filter(usuario=usuario)
            # Guardo la opcion "Todas" + las colecciones que tenga el usuario en "opciones"
            opciones = [("", "Todas")] + [(c.id, c.nombre_coleccion) for c in colecciones_usuario]
            self.fields["coleccion"].choices = opciones

class AgregarEntradaEnColeccionForm(forms.Form):
    colecciones = forms.ModelMultipleChoiceField(
        queryset=Coleccion.objects.none(),  # Se llenará dinámicamente
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Seleccionar colecciones donde desea guardar su entrada"
    )

    def __init__(self, *args, usuario=None, entrada=None, **kwargs):
        super().__init__(*args, **kwargs)

        # Si hay usuario, filtramos solo sus colecciones
        if usuario:
            self.fields["colecciones"].queryset = Coleccion.objects.filter(usuario=usuario)

        # Si hay entrada, marcamos las colecciones a las que ya pertenece
        if entrada:
            self.fields["colecciones"].initial = entrada.colecciones.all()
