#!/bin/bash

# Find and kill the Flask process
FLASK_PID=$(pgrep -f "flask run")
if [ ! -z "$FLASK_PID" ]; then
    echo "Stopping Flask server (PID: $FLASK_PID)..."
    kill -9 $FLASK_PID
    echo "Flask server stopped."
else
    echo "No Flask server is currently running."
fi

# Deactivate virtual environment if active
if [ -n "$VIRTUAL_ENV" ]; then
    deactivate
    echo "Virtual environment deactivated."
fi
