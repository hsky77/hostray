# hostray

[![Documentation Status](https://readthedocs.org/projects/hostray/badge/?version=latest)](https://hostray.readthedocs.io/en/latest/?badge=latest) [![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT) [![PyPI version](https://img.shields.io/pypi/dm/hostray.svg)](https://pypi.org/project/hostray/) [![PyPI version](https://img.shields.io/pypi/v/hostray.svg)](https://pypi.org/project/hostray/)

**hostray** is a pure python project adding simple, scalable, and configurable module framework and utilties to opensource web frameworks. It's currentlly based on [Tornado Web Server](https://www.tornadoweb.org/en/stable/)

**prerequest**: python 3.6+, pip

**Install** hostray with pip: ``pip install hostray``

## Hello world

create a minimal runable server project:
   * In command prompt, create a project named hello: `python3 -m hostray create hello`
   * Start the project: `python3 -m hostray start hello`
   * Open Browser views the response of hello api, [click](http://localhost:8888/hello)
   * To stop server, press **ctrl+c** in the command prompt

Read [documentation](https://hostray.readthedocs.io/en/latest/) for more information (still updating...)