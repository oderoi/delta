from setuptools import setup, find_packages

setup(
    name="delta",
    version="1.0.0",
    description="A lightweight CLI for running local LLMs using llama.cpp",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Oderoi",
    license="MIT",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.31.0",
        "duckduckgo-search>=3.0.0",
        "wikipedia>=1.4.0",
        "PyPDF2>=3.0.0",
        "click>=8.1.0",
        "tabulate>=0.9.0",
        "colorama>=0.4.6",
        "huggingface_hub>=0.20.0",
        "tqdm>=4.66.0",
        "psutil>=5.9.0",
        "nvidia-ml-py>=12.560.30; sys_platform=='linux' or sys_platform=='win32'",
    ],
    package_data={
        "delta": ["img/*.png"],
    },
    entry_points={"console_scripts": ["delta = delta.cli:cli"]},
)