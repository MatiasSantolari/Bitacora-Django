**Bitácora-Django** es una aplicación web diseñada para llevar un registro personal de entradas organizadas por colecciones. 
Es un sistema seguro y funcional que permite a los usuarios crear sus propias cuentas y gestionar su contenido.

## Características

- **Gestión de usuarios**:
  - Creación de cuentas de usuario.
  - Hash y encriptación de contraseñas para mayor seguridad.
  - Control de acceso a rutas específicas del sistema según el estado del usuario.

- **Entradas y colecciones**:
  - Creación y gestión de entradas en la bitácora.
  - Organización de entradas mediante colecciones personalizadas.
  - Entradas públicas visibles en la página principal y entradas privadas visibles únicamente para el creador.

- **Página principal**:
  - Vista de todas las entradas públicas de los usuarios registrados.

## Tecnologías utilizadas

- **Backend**: Django (Python).
- **DataBase**: PostgreSQL
- **Frontend**: HTML, CSS y Bootstrap.

## Instalación

1. Clona este repositorio
2. Navegar hasta el directorio del proyecto clonado
3. Crear y activar un entorno virtual
4. Instalar las dependencias --> pip install -r requirements.txt
5. Realizar las migraciones de la base de datos --> python manage.py migrate
6. Iniciar el servidor de desarrollo --> python manage.py runserver
7. Abrir tu navegador y acceder a http://127.0.0.1:8000
