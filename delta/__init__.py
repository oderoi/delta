"""
Delta - Access open source LLMs in your local machine

A CLI tool for running local large language models with support for
Wikipedia, arXiv, DuckDuckGo search, and document processing.
"""

import warnings
import sys

# Suppress the runpy warning globally
warnings.filterwarnings("ignore", message=".*found in sys.modules after import.*")
warnings.filterwarnings("ignore", category=RuntimeWarning, module="runpy")

from .cli import cli
from .__version__ import __version__