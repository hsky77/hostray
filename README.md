# hostray

[![Documentation Status](https://readthedocs.org/projects/hostray/badge/?version=latest)](https://hostray.readthedocs.io/en/latest/?badge=latest) [![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT) [![PyPI version](https://img.shields.io/pypi/v/hostray.svg)](https://pypi.org/project/hostray/)

**hostray** is a pure python project adding simple, scalable, and configurable module framework and utilties to opensource web frameworks. It's currently based on [Tornado Web Server](https://www.tornadoweb.org/en/stable/)

**prerequest**: python 3.6+, pip

**Install** hostray with pip: ``pip install hostray``

## Hello world

create a minimal runable server project:
   * In command prompt, create a project named hello: `python3 -m hostray create hello`
   * Start the project: `python3 -m hostray start hello`
   * Open Browser views the response of hello api, [http://localhost:8888/hello](http://localhost:8888/hello)
   * To stop server, press **ctrl+c** in the command prompt

Read [documentation](https://hostray.readthedocs.io/en/latest/) for more information (still updating...)

## Change log

* **0.7.5.1 - Apr. 15, 2020**:
  * Add missing dependency, [requests](https://requests.readthedocs.io/en/master/)

* **0.7.5 - Mar. 20, 2020**:

  * Use [aiohttp](https://github.com/aio-libs/aiohttp) for sending requests asynchronously.
  * Set logger level to Error when debug set to false in server_config.yaml.
  * Method dispose() of component classes become awaitable.
  * Add certification authority 'ca' parameter for ssl settings in server_config.yaml.
  * Fix bugs.

* **0.7.3 - Dec. 31, 2019**:

   * Bug Fix:

      * Arcpath (path in compressed file) might be incorrect when packing projects.
      * Changing test server port in unittest of **hostray** library to avoid conflict with default port 8888
      * The 'required' parameter of ConfigValidator classes does not work properly in all cases.

* **0.7.2 - Dec. 8, 2019**:

   * Initalizing github project.