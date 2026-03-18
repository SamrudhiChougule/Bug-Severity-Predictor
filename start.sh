#!/bin/bash
echo "Starting Bug Severity Predictor..."

# Start backend API in background
cd backend
python app.py &
BACKEND_PID=$!

# Wait for backend to initialize
sleep 3

# Open frontend in default browser
cd ..
if command -v xdg-open > /dev/null; then
    xdg-open frontend/index.html
elif command -v open > /dev/null; then
    open frontend/index.html
else
    echo "Please open frontend/index.html in your browser"
fi

echo "Backend started (PID: $BACKEND_PID) and frontend opened!"
echo "Press Ctrl+C to stop everything"

# Wait for user to stop
trap "kill $BACKEND_PID; exit" INT
wait
