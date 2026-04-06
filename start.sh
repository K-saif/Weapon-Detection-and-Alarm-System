#!/bin/bash
# Quick start script for Weapon Detection System

echo ""
echo "============================================"
echo "Weapon Detection System - Quick Start"
echo "============================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python3 is not installed"
    exit 1
fi

# Check if requirements are installed
echo "Checking dependencies..."
if ! python3 -m pip show streamlit &> /dev/null; then
    echo "Installing required packages..."
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "Error: Failed to install requirements"
        exit 1
    fi
fi

echo ""
echo "Select how to start:"
echo ""
echo "1. Start Streamlit Dashboard (Recommended)"
echo "2. Start Detection + Dashboard"
echo "3. Start Detection Only (CLI)"
echo "4. Exit"
echo ""

read -p "Enter your choice (1-4): " choice

case $choice in
    1)
        echo "Starting Streamlit Dashboard..."
        echo "Open: http://localhost:8501"
        streamlit run streamlit_app.py
        ;;
    2)
        echo ""
        echo "Starting detection pipeline..."
        echo "In another terminal, run: streamlit run streamlit_app.py"
        echo ""
        python3 main.py --source 0
        ;;
    3)
        echo "Starting detection pipeline..."
        python3 main.py --source 0
        ;;
    4)
        echo "Exiting..."
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac
