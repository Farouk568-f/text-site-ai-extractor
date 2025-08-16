# -*- coding: utf-8 -*-
"""
Vercel API endpoint for Text Site AI Extractor
"""

import sys
import os

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from article_api import app

# Export the Flask app for Vercel
if __name__ == "__main__":
    app.run()
