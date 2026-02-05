"""
The setup.py file is an essential part of packaging and distributing Python projects.
It defines project metadata, dependencies, and package configuration so the project
can be installed using pip in development and production environments.
"""

from setuptools import find_packages, setup
from typing import List


def get_requirements(file_path: str = "requirements.txt") -> List[str]:
    """
    Reads the requirements file and returns a clean list of dependencies,
    excluding editable installs like '-e .'.
    """
    requirements: List[str] = []

    try:
        with open(file_path, "r") as file:
            # read and process lines from the file
            for line in file.readlines():
                requirement = line.strip()

                # Ignore empty lines and editable install
                if requirement and requirement != "-e .":
                    requirements.append(requirement)

    except FileNotFoundError:
        raise FileNotFoundError("requirements.txt file not found.")

    return requirements


setup(
    name="Networksecurity",
    version="0.0.1",
    author="Nihal Jaiswal",
    author_email="nihaljaisawal1@gmail.com",  
    description="End-to-end MLOps pipeline for AI-powered network security detection",
    packages=find_packages(),
    install_requires=get_requirements(),
    python_requires=">=3.8",
)
