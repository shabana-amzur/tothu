#!/bin/bash

# AI Chat Application - Quick Start Script
# Project 1: Basic Chatbot

echo "=================================="
echo "  AI CHAT APPLICATION - PROJECT 1"
echo "=================================="
echo ""

# Colors
GREEN='\033[0.32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if in correct directory
if [ ! -f "requirements.txt" ]; then
    echo "Error: Please run this script from the project root directory (Tothu/)"
    exit 1
fi

echo -e "${BLUE}Checking environment...${NC}"

# Check Python
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}✓${NC} Python installed: $PYTHON_VERSION"
else
    echo -e "${YELLOW}✗${NC} Python 3 not found"
    exit 1
fi

# Check Node
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo -e "${GREEN}✓${NC} Node.js installed: $NODE_VERSION"
else
    echo -e "${YELLOW}✗${NC} Node.js not found"
    exit 1
fi

# Check virtual environment
if [ -d "venv" ]; then
    echo -e "${GREEN}✓${NC} Virtual environment exists"
else
    echo -e "${YELLOW}✗${NC} Virtual environment not found"
    exit 1
fi

# Check .env file
if [ -f ".env" ]; then
    echo -e "${GREEN}✓${NC} .env file exists"
else
    echo -e "${YELLOW}✗${NC} .env file not found"
    exit 1
fi

echo ""
echo -e "${BLUE}Starting servers...${NC}"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "Stopping servers..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit
}

trap cleanup INT TERM

# Start backend
echo -e "${BLUE}[1/2] Starting FastAPI Backend...${NC}"
cd backend
source ../venv/bin/activate
uvicorn main:app --reload --port 8001 > /tmp/backend.log 2>&1 &
BACKEND_PID=$!
cd ..

# Wait a moment for backend to start
sleep 3

# Check if backend is running
if kill -0 $BACKEND_PID 2>/dev/null; then
    echo -e "${GREEN}✓${NC} Backend started on http://localhost:8001"
else
    echo -e "${YELLOW}✗${NC} Backend failed to start. Check /tmp/backend.log"
    exit 1
fi

# Start frontend
echo -e "${BLUE}[2/2] Starting Next.js Frontend...${NC}"
cd frontend
npm run dev > /tmp/frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

# Wait a moment for frontend to start
sleep 5

# Check if frontend is running
if kill -0 $FRONTEND_PID 2>/dev/null; then
    echo -e "${GREEN}✓${NC} Frontend started on http://localhost:3000"
else
    echo -e "${YELLOW}✗${NC} Frontend failed to start. Check /tmp/frontend.log"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

echo ""
echo "=================================="
echo -e "${GREEN}✓ Both servers are running!${NC}"
echo "=================================="
echo ""
echo "URLs:"
echo "  • Frontend: http://localhost:3000"
echo "  • Backend:  http://localhost:8001"
echo "  • API Docs: http://localhost:8001/docs"
echo ""
echo "Logs:"
echo "  • Backend:  /tmp/backend.log"
echo "  • Frontend: /tmp/frontend.log"
echo ""
echo "Press Ctrl+C to stop all servers"
echo ""

# Keep script running
wait
