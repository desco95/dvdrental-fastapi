DVD Rental API

Sistema de Renta de DVDs desarrollado como proyecto académico.
Incluye una API REST para la gestión de rentas y una aplicación de escritorio como frontend.


Hecho por
Luis David Escobedo Ojeda
Juan Pablo Almaguer Gomez
Valeria Melissa Leilani Quintero Frausto
Luz Andrea Villalpando Casillas 

Ingeniería en Sistemas Computacionales
Instituto Tecnológico de León

Descripción
API REST para la gestión de rentas de DVDs utilizando FastAPI y PostgreSQL.
El sistema permite realizar la renta, devolución y cancelación de DVDs, así como la generación de reportes solicitados en la práctica.

El proyecto está dividido en Backend y Frontend, conforme a los requerimientos de la actividad.

Funcionalidades

Registrar rentas de DVDs
Devolver DVDs
Cancelar rentas
Consultar rentas por cliente
Generar reportes:

DVDs no devueltos
DVDs más rentados
Rentas realizadas por cliente
Ganancia generada por cada miembro del staff


Tecnologías Utilizadas

Backend: Python 3 + FastAPI
Base de datos: PostgreSQL
Frontend: Aplicación de escritorio en Python (Tkinter)
Contenedores: Docker y Docker Compose
Testing: Bash y Curl
CI/CD: GitHub Actions


Instalación
Opción 1: Docker Compose (Recomendado)
# Clonar repositorio
git clone <tu-repositorio>
cd dvdrental-fastapi
# Levantar servicios
docker-compose up -d


La API estará disponible en:
http://localhost:8000

Documentación automática:
http://localhost:8000/docs

Opción 2: Comandos Docker
# Crear red
docker network create dvdrental-network
# PostgreSQL
docker run -d \
--name dvdrental-db \
--network dvdrental-network \
-e POSTGRES_USER=postgres \
-e POSTGRES_PASSWORD=postgres \
-e POSTGRES_DB=dvdrental \
-p 5432:5432 \
postgres:15
# API
docker run -d \
--name dvdrental-api \
--network dvdrental-network \
-e DB_HOST=dvdrental-db \
-p 8000:8000 \
dvdrental-api:latest

API Endpoints
Base URL:
http://localhost:8000

Películas
GET    /api/films
GET    /api/films/{id}
GET    /api/films/search?title=palabra
GET    /api/films/category/{category}

Clientes
GET    /api/customers
GET    /api/customers/{id}

Staff
GET    /api/staff
GET    /api/staff/{id}

Rentas
GET    /api/rentals
POST   /api/rentals
PUT    /api/rentals/{id}/return
DELETE /api/rentals/{id}
GET    /api/rentals/customer/{customer_id}

Reportes
GET    /api/reports/unreturned-dvds
GET    /api/reports/most-rented
GET    /api/reports/staff-revenue
GET    /api/reports/staff-revenue/{staff_id}
GET    /api/reports/customer-rentals/{id}

Variables de Entorno

API
Variable	Default
DB_HOST	localhost
DB_PORT	5432
DB_USER	postgres
DB_PASSWORD	postgres
DB_NAME	dvdrental
PORT	8000

PostgreSQL
Variable	Default
POSTGRES_USER	postgres
POSTGRES_PASSWORD	postgres
POSTGRES_DB	dvdrental
Tests

Las pruebas se realizan utilizando Bash y Curl.
chmod +x tests/test-api.sh
./tests/test-api.sh
Estas pruebas se ejecutan automáticamente mediante GitHub Actions.

Aplicación de Escritorio
El frontend es una aplicación de escritorio desarrollada en Python.
cd desktop-app
pip install -r requirements-desktop.txt
python app.py
La aplicación se conecta a la API REST para realizar todas las operaciones.

Comandos Útiles

Reiniciar contenedores:
docker-compose restart

Detener servicios:
docker-compose down

Eliminar todo (incluyendo datos):
docker-compose down -v

Estructura del Proyecto
dvdrental-fastapi/
├── backend/
├── postgres/
│   └── init-db/
├── desktop-app/
├── tests/
├── .github/workflows/
└── docker-compose.yml
