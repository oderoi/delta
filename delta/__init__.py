"""
Delta - Access open source LLMs in your local machine

A CLI tool for running local large language models with support for
Wikipedia, arXiv, DuckDuckGo search, and document processing.
"""

__version__ = "1.0.0"
__author__ = "Nile AGI"
__email__ = "support@nileagi.com"

from .delta import main

__all__ = ["main"] 