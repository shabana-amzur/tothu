#!/bin/bash
# Start Both Backend and Frontend Servers

echo "🚀 Starting Backend Server..."
cd "$(dirname "$0")"
./start_backend.sh > /tmp/backend.log 2>&1 &
BACKEND_PID=$!
echo "✅ Backend started (PID: $BACKEND_PID) - Logs: /tmp/backend.log"

echo ""
echo "🎨 Starting Frontend Server..."
./start_frontend.sh > /tmp/frontend.log 2>&1 &
FRONTEND_PID=$!
echo "✅ Frontend started (PID: $FRONTEND_PID) - Logs: /tmp/frontend.log"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎉 All servers started successfully!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📍 Backend:  http://localhost:8001"
echo "📍 Frontend: http://localhost:3000"
echo "📍 API Docs: http://localhost:8001/docs"
echo ""
echo "📋 Backend PID:  $BACKEND_PID"
echo "📋 Frontend PID: $FRONTEND_PID"
echo ""
echo "To stop servers: kill $BACKEND_PID $FRONTEND_PID"
echo "Or use: pkill -f uvicorn && pkill -f 'next dev'"
