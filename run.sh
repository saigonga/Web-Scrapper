#!/bin/bash

# Define virtual environment directory
VENV_DIR="venv"

# check if we are on windows (git bash/cygwin/wsl) or strict unix
# mostly likely running in git bash on windows based on user usage
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    PYTHON_CMD="python"
    VENV_ACTIVATE="$VENV_DIR/Scripts/activate"
else
    PYTHON_CMD="python3"
    VENV_ACTIVATE="$VENV_DIR/bin/activate"
fi

# 1. Create virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    $PYTHON_CMD -m venv $VENV_DIR
fi

# 2. Activate virtual environment
source $VENV_ACTIVATE

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Install playwright browsers
echo "Installing Playwright browsers..."
playwright install chromium

# 3. Start web server
echo "Starting web server on http://localhost:8000..."
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
