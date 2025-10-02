from setuptools import setup, find_packages

setup(
    name="delta-ai",
    version="0.2.0",  # Bump from your current
    author="Your Name",
    description="Standalone LLM runner using llama.cpp, inspired by Ollama",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "delta = delta.cli:cli"
        ]
    },
    install_requires=[
        "llama-cpp-python>=0.2.78",
        "huggingface-hub>=0.20.3",
        "click>=8.1.7",
        "wikipedia>=1.4.0",
    ],
    python_requires=">=3.8",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)