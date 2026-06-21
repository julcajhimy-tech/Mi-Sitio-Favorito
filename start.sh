#!/bin/bash

# Inicializa la base de datos en cada despliegue
echo "Inicializando la base de datos..."
python -m scripts.init_db

# Inicia el servidor de la aplicación
echo "Iniciando la aplicación..."
python -m gunicorn --worker-class gevent -w 1 run:app