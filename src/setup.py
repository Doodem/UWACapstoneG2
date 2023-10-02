from setuptools import find_packages, setup

setup(
        name="TendersWA",
        packages=find_packages(),
        version="0.1.0",
        description="TendersWA python library for NLP applications",
        author="Max Chatfield, Limin Deng, Mitchell Doody-Burras, Joyce Ye, Andre Italiano, Enam Shaikh",
        install_requires=["networkx"]
)
