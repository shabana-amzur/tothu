#!/bin/bash
# Start Backend Server

cd "$(dirname "$0")/backend"
source ../venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8001
