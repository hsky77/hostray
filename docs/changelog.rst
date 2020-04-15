Change log
=====================================

* **0.7.5.1 - Apr. 15, 2020**:
  * Add missing dependency, `requests <https://requests.readthedocs.io/en/master/>`__

* **0.7.5 - Mar. 20, 2020**:

  * Use `aiohttp <https://github.com/aio-libs/aiohttp>`__ for sending requests asynchronously.
  * Set logger level to Error when debug set to false in server_config.yaml.
  * Method dispose() of component classes become awaitable.
  * Add certification authority 'ca' parameter for ssl settings in server_config.yaml.
  * Fix bugs.

* **0.7.3 - Dec 31, 2019**:

   * Bug Fix:

      * Arcpath (path in compressed file) might be incorrect when packing projects.
      * Changing test server port in unittest of **hostray** library to avoid conflict with default port 8888
      * The 'required' parameter of ConfigValidator classes does not work properly in all cases.

* **0.7.2 - Dec 8, 2019**:

   * Initalizing github project.