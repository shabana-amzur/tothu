#!/bin/bash
# Stop All Servers

echo "🛑 Stopping servers..."

# Stop backend
pkill -f "uvicorn main:app" && echo "✅ Backend stopped" || echo "❌ Backend not running"

# Stop frontend
pkill -f "next dev" && echo "✅ Frontend stopped" || echo "❌ Frontend not running"

echo ""
echo "✨ All servers stopped"
