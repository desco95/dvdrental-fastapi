DVD Rental – Aplicación de Escritorio

Aplicación de escritorio con interfaz gráfica para gestionar el sistema de rentas de DVDs mediante una API REST.

Características

Interfaz gráfica desarrollada con Tkinter

Gestión de películas

Administración de clientes

Creación, devolución y cancelación de rentas

Visualización de reportes

Conexión configurable a la API REST

Requisitos

Python 3.8 o superior

Tkinter (incluido por defecto con Python)

Requests

Instalación
# Navegar a la carpeta de la aplicación
cd desktop-app

# Instalar dependencias
pip install -r requirements-desktop.txt

# Opcional: usar entorno virtual (recomendado)
python -m venv venv
# En Linux/Mac
source venv/bin/activate
# En Windows
venv\Scripts\activate

pip install -r requirements-desktop.txt

Uso
1. Iniciar la API

Antes de ejecutar la aplicación de escritorio, asegúrate de que la API esté en ejecución.

# Con Docker Compose
docker-compose up -d


Verifica que la API esté activa:

curl http://localhost:8000/health

2. Ejecutar la Aplicación
python app.py

Interfaz de Usuario

La aplicación está organizada en cuatro secciones principales:

Películas

Listar todas las películas disponibles

Buscar películas por título

Consultar información detallada

Clientes

Listar clientes registrados

Ver información del cliente

Consultar historial de rentas

Rentas

Crear nuevas rentas

Devolver DVDs

Cancelar rentas activas

Consultar todas las rentas

Reportes

DVDs no devueltos

Películas más rentadas

Ganancias generadas por el staff

Configuración
URL de la API

En la ventana principal de la aplicación se puede modificar la URL de conexión a la API.

Ejemplos comunes:

Local:

http://localhost:8000


Después de modificar la URL, utilizar el botón Probar Conexión para verificar el acceso.

Funciones Principales
Crear Renta

Ir a la pestaña Rentas

Ingresar:

ID del cliente

ID de la película

ID del staff

Presionar Crear Renta

Devolver DVD

En la pestaña Rentas, listar las rentas

Seleccionar una renta activa

Presionar Devolver

El sistema calcula automáticamente el cobro correspondiente

Ver Reportes

Ir a la pestaña Reportes

Seleccionar el tipo de reporte

Los resultados se muestran en pantalla

Solución de Problemas
No se puede conectar a la API
curl http://localhost:8000/health


Si no responde:

docker-compose restart api

Error: No module named 'tkinter'

En Linux:

sudo apt-get install python3-tk


En Windows y macOS, Tkinter viene incluido con Python.

Error de conexión (Connection refused)

Verificar que la API esté ejecutándose

Revisar la URL configurada

Confirmar que Docker esté activo

Datos de Prueba

Para probar la aplicación se pueden utilizar los siguientes valores:

Clientes: IDs 1, 2, 3

Películas: IDs 1, 2, 3

Staff: IDs 1 o 2

Flujo General de Uso

Consultar películas disponibles

Crear una renta

Registrar la devolución del DVD

Consultar reportes