from django.urls import path
from django.contrib.auth.views import LogoutView

from . import views

app_name = 'bitacora'
urlpatterns = [
    # ex: bitacora/iniciar_sesion/
    path('iniciar_sesion/', views.iniciar_sesion, name='iniciar_sesion'),
    # ex: bitacora/registrar_usuario/
    path('registrar_usuario/', views.registrar_usuario, name='registrar_usuario'),
    # ex: bitacora/logout
    path('logout/', LogoutView.as_view(next_page='/bitacora/iniciar_sesion'), name='logout'), #django proporciona una vista predefinida para el cierre de sesion
    # ex: /bitacora/pagina_principal/
    path('pagina_principal', views.pagina_principal, name='pagina_principal'),
    # ex: /bitacora/mis__entradas
    path('mis_entradas/', views.mis_entradas, name='mis_entradas'),
    # ex: /bitacora/agregar_entrada/
    path('agregar_entrada/',views.agregar_entrada, name='agregar_entrada'),
    # ex: /bitacora/editar_entrada/1
    path('editar_entrada/<int:entrada_id>/', views.editar_entrada, name='editar_entrada'),
    # ex: /bitacora/eliminar_entrada/1
    path('eliminar_entrada/<int:entrada_id>/', views.eliminar_entrada, name='eliminar_entrada'),
    # ex: /bitacora/mis_colecciones
    path('mis_colecciones', views.mis_colecciones, name='mis_colecciones'),
    # ex: /bitacora/agregar_coleccion
    path('agregar_coleccion', views.agregar_coleccion, name='agregar_coleccion'),
    # ex: /bitacora/editar_coleccion/1
    path('editar_coleccion/<int:coleccion_id>/', views.editar_coleccion, name='editar_coleccion'),
    # ex: /bitacora/eliminar_coleccion/1
    path('eliminar_coleccion/<int:coleccion_id>/', views.eliminar_coleccion, name='eliminar_coleccion'),
    # ex: /bitacora/agregar_entrada_a_coleccion/1
    path('agregar_entrada_a_coleccion/<int:entrada_id>/', views.agregar_entrada_a_coleccion, name='agregar_entrada_a_coleccion'),
]

