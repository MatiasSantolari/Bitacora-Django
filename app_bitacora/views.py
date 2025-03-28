from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, get_user_model
from django.contrib.auth.decorators import login_required
from django import forms
from django.db.models import Q

from .models import Usuario, Entrada, Coleccion
from .forms import LoginForm, RegistrarUsuarioForm, EntradaForm, ColeccionForm, FiltrosEntradaForm, AgregarEntradaEnColeccionForm
from .validaciones import validar_email, validar_username, validar_password, validar_fecha_no_futura, validar_campo_no_repetido

# Obtengo el modelo de usuario personalizado
Usuario = get_user_model()

def index(request):
    return HttpResponse("la app 'bitacora' se creo correctamente")

def iniciar_sesion(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            # Accede a los datos del formulario
            nombre = form.cleaned_data['nombre']
            password = form.cleaned_data['password']

            # Usar authenticate para validar credenciales
            usuario = authenticate(request, username=nombre, password=password)

            if usuario is not None:  # Usuario autenticado correctamente
                login(request, usuario)  # Inicia la sesión
                messages.success(request, f"Bienvenido {usuario.username}!")
                return redirect('/bitacora/pagina_principal')
            else:
                messages.error(request, "Las credenciales no son válidas. Intente nuevamente.")
        else:
            messages.error(request, "Formulario inválido. Por favor, verifica los datos.")
    else:  # Si es GET, renderiza el formulario vacío
        form = LoginForm()
    return render(request, 'app_bitacora/login.html', {'form': form})

def registrar_usuario(request):
    if request.method == 'POST':
        # Extraemos los datos enviados por el formulario
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        repeated_password = request.POST.get('repeated_password')
        pais = request.POST.get('pais')

        # Validaciones manuales
        errores = False  # Para rastrear si hubo errores

        # Validar username
        try:
            validar_username(username)
        except forms.ValidationError as e:
            errores = True
            messages.error(request, e.message)

        # Validar email
        try:
            validar_email(email)
        except forms.ValidationError as e:
            errores = True
            messages.error(request, e.message)

        # Validar contraseñas
        try:
            validar_password(password, repeated_password)
        except forms.ValidationError as e:
            errores = True
            messages.error(request, e.message)

        # Si hay errores, no procesamos el formulario
        if errores:
            return render(request, 'app_bitacora/registrar_usuario.html', {
                'form': RegistrarUsuarioForm(request.POST)
            })

        # Si no hay errores, creamos el usuario
        usuario = Usuario(
            username=username,
            email=email,
            pais=pais
        )
        usuario.set_password(password)  # Hasheamos la contraseña
        usuario.save()

        # Mensaje de éxito y redirección
        messages.success(request, "Usuario registrado exitosamente.")
        return redirect('bitacora:iniciar_sesion')

    else:
        form = RegistrarUsuarioForm()

    return render(request, 'app_bitacora/registrar_usuario.html', {'form': form})

def pagina_principal(request):
    entradas = Entrada.objects.filter(tipo_entrada = 'publica').order_by('-fecha_entrada')
    context = { "entradas": entradas }
    return render(request, 'app_bitacora/homepage.html', context)

@login_required
def mis_entradas(request):
    form = FiltrosEntradaForm(usuario=request.user, data=request.GET)
    # Filtrar solo las entradas del usuario autenticado
    entradas = Entrada.objects.filter(usuario=request.user).order_by('-fecha_entrada')

    # Lógica de los filtros
    if form.is_valid():
        # Filtrar por colección si el usuario seleccionó una
        coleccion_id = form.cleaned_data.get("coleccion")
        if coleccion_id:
            entradas = entradas.filter(colecciones=coleccion_id)

        # Filtrar por tipo de entrada
        tipo_entrada = form.cleaned_data.get("tipo_entrada")
        if tipo_entrada:
            entradas = entradas.filter(tipo_entrada=tipo_entrada)

        busqueda = form.cleaned_data.get("busqueda_x_detalle_entrada")
        if busqueda:
            palabras = busqueda.split()  # Divide la búsqueda en palabras
            consulta = Q() # Creo una consulta con Q() para cada palabra en palabras
            for palabra in palabras:
                consulta &= Q(detalle_entrada__icontains=palabra)  # Filtra por cada palabra y con icontains pueden ser coincidencias parciales(asi evito tener que trabajar con coincidencias totales en la busqueda)
                # Todas las palabras sueltas deben coincidir para que la entrada pase el filtro y se muestre
                # Esto lo hago gracias a &= que funciona como un AND y asegura que todas las palabras de la búsqueda estén en detalle_entrada.
            entradas = entradas.filter(consulta)

    context = {"form": form, "entradas": entradas}
    return render(request, 'app_bitacora/mis_entradas.html', context)

def agregar_entrada(request):
    if request.method == 'POST':
        form = EntradaForm(request.POST, request.FILES)
        if form.is_valid():
            # Accede a los datos del formulario
            detalle = form.cleaned_data['detalle_entrada']
            fecha = form.cleaned_data['fecha_entrada']
            tipo = form.cleaned_data['tipo_entrada']
            imagen = form.cleaned_data['imagen']

            # Validaciones manuales
            errores = False  # Para rastrear si hubo errores

            # Validar que la fecha no sea futura
            try:
                validar_fecha_no_futura(fecha)
            except forms.ValidationError as e:
                errores = True
                messages.error(request, e.message)

            # Si hay errores, no procesamos el formulario
            if errores:
                return render(request, 'app_bitacora/agregar_entrada.html', {
                    'form': EntradaForm(request.POST, request.FILES)
                })

            # Si no hay errores, creamos el usuario
            usuario = request.user # Asociar la entrada al usuario autenticado

            # Crear una nueva entrada
            Entrada.objects.create(
                detalle_entrada=detalle,
                tipo_entrada=tipo,
                fecha_entrada=fecha,
                usuario=usuario,
                imagen=imagen,
            )
            return redirect('/bitacora/mis_entradas')

    else: #si resulta ser un get
        form = EntradaForm()
    return render(request, 'app_bitacora/agregar_entrada.html', {'form': form})

@login_required
def editar_entrada(request, entrada_id):
    entrada = get_object_or_404(Entrada, id=entrada_id)

    # Asegurarse de que el usuario autenticado es el propietario de la entrada
    if entrada.usuario != request.user:
        messages.error(request, "No tienes permiso para editar esta entrada.")
        return redirect('bitacora:mis_entradas')

    if request.method == 'POST':
        form = EntradaForm(request.POST, request.FILES, instance=entrada)
        if form.is_valid():
            # Accede a los datos del formulario
            detalle = form.cleaned_data['detalle_entrada']
            fecha = form.cleaned_data['fecha_entrada']
            tipo = form.cleaned_data['tipo_entrada']
            imagen = form.cleaned_data.get('imagen')  # Puede ser None si no se sube una nueva imagen

            # Validaciones manuales
            errores = False

            # Validar que la fecha no sea futura
            try:
                validar_fecha_no_futura(fecha)
            except forms.ValidationError as e:
                errores = True
                messages.error(request, e.message)

            # Si hay errores, renderizamos el formulario nuevamente
            if errores:
                return render(request, 'app_bitacora/editar_entrada.html', {'form': form})

            # Actualizar los datos de la entrada
            entrada.detalle_entrada = detalle
            entrada.fecha_entrada = fecha
            entrada.tipo_entrada = tipo
            if imagen:  # Solo actualizar la imagen si se sube una nueva
                entrada.imagen = imagen

            # Guardar la entrada
            entrada.save()

            # Mensaje de éxito
            messages.success(request, "La entrada se actualizó correctamente.")
            return redirect('bitacora:mis_entradas')
        else:
            # Si el formulario tiene errores
            messages.error(request, "Por favor corrige los errores en el formulario.")
    else:  # Si es un GET
        form = EntradaForm(instance=entrada)

    return render(request, 'app_bitacora/editar_entrada.html', {'form': form})

@login_required
def eliminar_entrada(request, entrada_id):
    entrada = get_object_or_404(Entrada, id=entrada_id)

    # Asegurarse de que el usuario autenticado es el propietario de la entrada
    if entrada.usuario != request.user:
        messages.error(request, "No tienes permiso para eliminar esta entrada.")
        return redirect('bitacora:mis_entradas')

    # Si la solicitud es POST, eliminar la entrada
    if request.method == "POST":
        entrada.delete()
        messages.success(request, "Entrada eliminada correctamente.")
        return redirect('bitacora:mis_entradas')

    # Si es GET, redirigir a la lista (en caso de intento directo en la URL)
    messages.warning(request, "No se ha confirmado la eliminación de la entrada.")
    return redirect('bitacora:mis_entradas')

@login_required
def agregar_entrada_a_coleccion(request, entrada_id):
    entrada = get_object_or_404(Entrada, id=entrada_id)

    if request.method == "POST":
        form = AgregarEntradaEnColeccionForm(request.POST, usuario=request.user, entrada=entrada)
        if form.is_valid():
            # Usamos set() para actualizar solo las colecciones elegidas
            entrada.colecciones.set(form.cleaned_data["colecciones"])
            return redirect("bitacora:mis_entradas")  # Volver a la página de entradas
    else:
        form = AgregarEntradaEnColeccionForm(usuario=request.user, entrada=entrada)

    return render(request, "app_bitacora/agregar_entrada_en_coleccion.html", {"form": form, "entrada": entrada})


@login_required()
def mis_colecciones(request):
    # Filtrar solo las colecciones del usuario autenticado
    colecciones = Coleccion.objects.filter(usuario=request.user).order_by('nombre_coleccion')
    context = {"colecciones": colecciones}
    return render(request, 'app_bitacora/mis_colecciones.html', context)

@login_required()
def agregar_coleccion(request):
    if request.method == 'POST':
        form = ColeccionForm(request.POST)
        if form.is_valid():
            # Accede a los datos del formulario
            nombre = form.cleaned_data['nombre_coleccion']
            detalle = form.cleaned_data['detalle_coleccion']

            # Extraigo los nombres de las colecciones ya existentes del usuario
            lista_nombres = list(Coleccion.objects.filter(usuario=request.user).values_list('nombre_coleccion', flat=True))

            # Validaciones manuales
            errores = False  # Para rastrear si hubo errores

            # Validar que el nombre de la colección no se repita
            try:
                validar_campo_no_repetido(nombre, lista_nombres)
            except forms.ValidationError as e:
                errores = True
                messages.error(request, e.message)

            # Si hay errores, no procesamos el formulario
            if errores:
                return render(request, 'app_bitacora/agregar_coleccion.html', {
                    'form': ColeccionForm(request.POST)
                })

            # Si no hay errores, creamos el usuario
            usuario = request.user  # Asociar la coleccion al usuario autenticado

            # Crear una nueva coleccion
            Coleccion.objects.create(
                nombre_coleccion = nombre,
                detalle_coleccion = detalle,
                usuario = usuario,
            )
            return redirect('/bitacora/mis_colecciones')
    else:
        form = ColeccionForm()
    return render(request, 'app_bitacora/agregar_coleccion.html',{'form': form})

@login_required
def editar_coleccion(request, coleccion_id):
    coleccion = get_object_or_404(Coleccion, id=coleccion_id)

    # Me aseguro que el usuario autenticado es el propietario de la coleccion
    if coleccion.usuario != request.user:
        messages.error(request, "No tienes permiso para editar esta coleccion.")
        return redirect('bitacora:mis_colecciones')

    # Guardo el nombre original antes de procesar el formulario
    nombre_original = coleccion.nombre_coleccion

    if request.method == 'POST':
        form = ColeccionForm(request.POST, request.FILES, instance=coleccion)
        if form.is_valid():
            # Accede a los datos del formulario
            nombre = form.cleaned_data['nombre_coleccion']
            detalle = form.cleaned_data['detalle_coleccion']

            # Extraigo los nombres de las colecciones ya existentes del usuario
            lista_nombres = list(
                Coleccion.objects.filter(usuario=request.user).values_list('nombre_coleccion', flat=True))

            # Validaciones manuales
            errores = False

            # Validar que el nombre de la colección no se repita
            if nombre != nombre_original: # Con esto aseguro que no revise en el caso que el usuario no edito el nombre de la coleccion
                print("entro al if, entonces nombre != coleccion.nombre_coleccion")
                try:
                    validar_campo_no_repetido(nombre, lista_nombres)
                except forms.ValidationError as e:
                    errores = True
                    messages.error(request, e.message)
            else:
                errores = False

            # Si hay errores, renderizamos el formulario nuevamente
            if errores:
                return render(request, 'app_bitacora/editar_coleccion.html', {'form': form})

            # Actualizar los datos de la entrada
            coleccion.nombre_coleccion = nombre
            coleccion.detalle_coleccion = detalle

            # Guardar la coleccion
            coleccion.save()

            # Mensaje de éxito
            messages.success(request, "La coleccion se actualizó correctamente.")
            return redirect('bitacora:mis_colecciones')
        else:
            # Si el formulario tiene errores
            messages.error(request, "Por favor corrige los errores en el formulario.")
    else:  # Si es un GET
        form = ColeccionForm(instance=coleccion)

    return render(request, 'app_bitacora/editar_coleccion.html', {'form': form})

@login_required
def eliminar_coleccion(request, coleccion_id):
    coleccion = get_object_or_404(Coleccion, id=coleccion_id)

    # Asegurarse de que el usuario autenticado es el propietario de la coleccion
    if coleccion.usuario != request.user:
        messages.error(request, "No tienes permiso para eliminar esta coleccion.")
        return redirect('bitacora:mis_colecciones')

    # Si la solicitud es POST, eliminar la coleccion
    if request.method == "POST":
        coleccion.delete()
        messages.success(request, "Coleccion eliminada correctamente.")
        return redirect('bitacora:mis_colecciones')

    # Si es GET, redirigir a la lista (en caso de intento directo en la URL)
    messages.warning(request, "No se ha confirmado la eliminación de la coleccion.")
    return redirect('bitacora:mis_colecciones')
