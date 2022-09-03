from setuptools import setup, find_packages

setup(
    name='ibwebapiclient',
    version='0.1.0',
    packages=find_packages(include=['ibwebapiclient']),
    install_requires=[
        "requests",
        "websocket-client",
        "coloredlogs",
        "pydantic"
    ]
)
