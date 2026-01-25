#!/bin/bash

# Default port
DEFAULT_PORT=8000
# List of alternative ports to try
ALTERNATE_PORTS=(8001 8002 8003)

# Function to check if a port is in use
is_port_in_use() {
  lsof -i :$1 &> /dev/null
  return $?
}

# Function to kill the process using a port
kill_port_process() {
  PID=$(lsof -t -i :$1)
  if [ -n "$PID" ]; then
    echo "Port $1 is in use by process $PID. Terminating process..."
    kill -9 $PID
    echo "Process $PID terminated."
  else
    echo "Port $1 is not in use."
  fi
}

# Try to start the server on the default port
is_port_in_use $DEFAULT_PORT
if [ $? -eq 0 ]; then
  kill_port_process $DEFAULT_PORT
fi

echo "Starting server on port $DEFAULT_PORT..."
uvicorn backend.user-service.main:app --host 0.0.0.0 --port $DEFAULT_PORT &

# Wait for a few seconds to check if the server started successfully
sleep 5
is_port_in_use $DEFAULT_PORT
if [ $? -ne 0 ]; then
  echo "Failed to start server on port $DEFAULT_PORT. Trying alternate ports..."
  for PORT in "${ALTERNATE_PORTS[@]}"; do
    is_port_in_use $PORT
    if [ $? -ne 0 ]; then
      echo "Starting server on port $PORT..."
      uvicorn backend.user-service.main:app --host 0.0.0.0 --port $PORT &
      sleep 5
      is_port_in_use $PORT
      if [ $? -eq 0 ]; then
        echo "Server started successfully on port $PORT."
        exit 0
      fi
    fi
  done
  echo "Failed to start server on all ports. Please check for issues."
  exit 1
else
  echo "Server started successfully on port $DEFAULT_PORT."
fi