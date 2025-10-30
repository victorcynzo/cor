#!/usr/bin/env python3
"""
Cor Gaze Detection Library - Main CLI Entry Point
Allows running: python -m cor <arguments>
"""

import sys
from . import cli

if __name__ == "__main__":
    sys.exit(cli())