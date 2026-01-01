#!/bin/bash

# Start PostgreSQL container
docker start password-manager-db

# Start Flask app container
docker start passwordmanager-app

# Show logs for PostgreSQL container in background
docker logs -f password-manager-db &

# Show logs for Flask app container (foreground)
docker logs -f passwordmanager-app
