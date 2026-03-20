#!/usr/bin/env python3
"""
SOL — Your Local AI Friend (v2.0)
===================================
Backward-compatible entry point. Launches the new modular SOL.
"""

import os
import sys

# Add the src directory to the path so sol package is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from sol.app import SolApp

if __name__ == "__main__":
    SolApp(base_dir=os.path.dirname(os.path.abspath(__file__))).run()
