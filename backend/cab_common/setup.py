from setuptools import setup

setup(
    name="cab_common",
    version="0.1.0",
    packages=["cab_common_auth"],
    install_requires=[
        "python-keycloak",
    ],
)
