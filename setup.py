from setuptools import setup, find_packages

setup(
    name="codeverse",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.68.0",
        "uvicorn>=0.15.0",
        "pydantic>=1.8.0",
        "libcst>=0.3.19",
    ],
) 