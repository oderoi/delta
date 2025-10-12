#!/bin/bash
# One-liner fix for Delta phone installation issues
# Run this if you get "ModuleNotFoundError: No module named 'click'"

echo "🔧 Fixing Delta phone installation..."

# Install missing dependencies
pip3 install click requests tabulate colorama huggingface_hub tqdm psutil

# Test the fix
if python3 -c "import click; from delta.cli import cli; print('✅ Fixed!')" 2>/dev/null; then
    echo "🎉 Delta is now working!"
    echo "Use: python3 -m delta.cli --help"
else
    echo "❌ Still having issues? Try:"
    echo "python3 quick_phone_fix.py"
fi
