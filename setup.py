from setuptools import setup, find_packages
import os

# Read the README file for long description
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements from requirements.txt
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="delta-ai",
    version="1.0.0",
    author="Nile AGI",
    author_email="support@nileagi.com",
    description="Access open source LLMs in your local machine with CLI support",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/oderoi/delta",
    project_urls={
        "Bug Reports": "https://github.com/oderoi/delta/issues",
        "Source": "https://github.com/oderoi/delta",
        "Documentation": "https://nileagi.com/products/delta",
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Systems Administration",
        "Topic :: Utilities",
    ],
    python_requires=">=3.8",
    packages=find_packages(),
    install_requires=read_requirements(),
    entry_points={
        "console_scripts": [
            "delta=delta.delta:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.md", "*.txt", "*.html"],
    },
    keywords="ai, llm, local, inference, ollama, cli, artificial intelligence, machine learning",
    zip_safe=False,
) 