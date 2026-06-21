#!/bin/bash

# Inicializa la base de datos en cada despliegue
echo "Inicializando la base de datos..."
python -m scripts.init_db
echo "Creando usuarios desde variables de entorno (si no existen)..."
python -m scripts.seed

# Inicia el servidor de la aplicación
echo "Iniciando la aplicación..."
python -m gunicorn --worker-class geventwebsocket.gunicorn.workers.GeventWebSocketWorker -w 1 run:app