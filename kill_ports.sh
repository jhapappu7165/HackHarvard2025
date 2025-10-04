#!/bin/bash

# Kill all processes running on common development ports
echo "Killing processes on common development ports..."

# Kill processes on port 5000 (Flask)
echo "Killing processes on port 5000..."
lsof -ti:5000 | xargs -r kill -9

# Kill processes on port 3000 (React/Node)
echo "Killing processes on port 3000..."
lsof -ti:3000 | xargs -r kill -9

# Kill processes on port 5173 (Vite)
echo "Killing processes on port 5173..."
lsof -ti:5173 | xargs -r kill -9

# Kill processes on port 5174 (Vite alternative)
echo "Killing processes on port 5174..."
lsof -ti:5174 | xargs -r kill -9

# Kill processes on port 8000 (Django/other)
echo "Killing processes on port 8000..."
lsof -ti:8000 | xargs -r kill -9

# Kill processes on port 8080 (Tomcat/other)
echo "Killing processes on port 8080..."
lsof -ti:8080 | xargs -r kill -9

# Kill any Python Flask processes
echo "Killing Python Flask processes..."
pkill -f "python app.py"
pkill -f "flask run"

# Kill any Node.js processes
echo "Killing Node.js processes..."
pkill -f "node"
pkill -f "npm"
pkill -f "pnpm"

echo "Port cleanup complete!"

