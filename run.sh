#!/bin/bash

cd backend/
echo "Initializing the environment..."

source venv/bin/activate
ENV_FILE=".env"

sleep 2

echo "Which database you want to proceed with?"
echo "1. postgresql"
echo "2. mongodb"
read choice
echo "Your choice is $choice"

case $choice in
  1)
    DB_TYPE="postgresql"
    ;;
  2)
    DB_TYPE="mongodb"
    ;;
  *)
    echo "Enter valid input"
    exit 1
    ;;
esac

echo "$DB_TYPE"

if grep -q "^DATABASE_TYPE=" "$ENV_FILE"; then
  sed -i.bak "s|^DATABASE_TYPE=.*|DATABASE_TYPE=$DB_TYPE|" "$ENV_FILE"
else
  echo "DATABASE_TYPE=$DB_TYPE" >> "$ENV_FILE"
fi

rm -f .env.bak
echo "DATABASE_TYPE set to $DB_TYPE in .env file"

echo "Initializing the backend..."
sleep 2
python3 app.py
