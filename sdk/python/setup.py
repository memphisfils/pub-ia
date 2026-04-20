from setuptools import setup, find_packages

setup(
    name="pub-ia-sdk",
    version="0.1.0",
    description="Pub-IA SDK for integrating ad monetization into AI chat applications",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=["requests>=2.28"],
)
