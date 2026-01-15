# postgres/Dockerfile
FROM postgres:15

# Copiar el script SQL y los archivos de datos
COPY init-db/ /docker-entrypoint-initdb.d/

# El script restore.sql espera los archivos en una ruta específica
# Crear enlace simbólico para que funcione
RUN mkdir -p /docker-entrypoint-initdb.d/data

# Dar permisos
RUN chmod -R 755 /docker-entrypoint-initdb.d

EXPOSE 5432