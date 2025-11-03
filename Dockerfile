# Usa una imagen base de Python
FROM python:3.11-slim

# Establecer el directorio de trabajo
WORKDIR /app

# Copiar los archivos del proyecto al contenedor
COPY . /app

# Instalar dependencias
RUN pip install --no-cache-dir flask firebase-admin gunicorn

# Exponer el puerto que usará Flask
EXPOSE 5000

# Comando para ejecutar la app usando Gunicorn (más estable que flask run)
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "prueba3:app"]
