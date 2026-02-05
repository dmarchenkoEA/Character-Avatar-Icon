#!/bin/bash
cd "$(dirname "$0")"

# Create venv if it doesn't exist
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi

# Install deps and run UI
.venv/bin/pip install -q Pillow requests cairosvg gradio
.venv/bin/python ui.py
