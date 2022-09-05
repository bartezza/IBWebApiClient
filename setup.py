from setuptools import find_packages, setup

if __name__ == "__main__":
    setup(name='ibwebapiclient',
          version='0.1.0',
          packages=find_packages(include=['ibwebapiclient']),
          install_requires=[
              "requests", "websocket-client", "coloredlogs", "pydantic"
          ])
