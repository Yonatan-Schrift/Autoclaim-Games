#!/bin/bash

# --- Check for Python ---
if ! command -v python3 &> /dev/null; then
    echo "-!- Python isn't installed, please install Python 3.11 or later."
    exit 1
fi

# --- Create virtual environment ---
echo "--- Creating a virtual Python environment for the project..."
python3 -m venv .venv

# --- Activate venv ---
source .venv/bin/activate

# --- Install requirements ---
echo "--- Installing project requirements..."
pip install --upgrade pip > /dev/null
pip install -r requirements.txt > /dev/null
python -m playwright install > /dev/null

echo ""
echo "Successfully installed the project requirements!"
echo ""
echo "Run the script with:   python main.py --help"
echo ""
echo "!!! Don't forget to update the environment file with your credentials!"
echo ""

# --- End ---
read -p "Press Enter to exit..."