Modules Framework
*****************************

.. contents:: Table of Contents

Reserved Modules
=============================

**hostray** project reserves the directories named **controller**, **component**, and **unit_test** as the modules of functionalities, rest apis, and unit testing cases. 
It's very similar to how python recognizes the packages, **hostray** load the modules with the directory contains ``__init__.py`` that defines specific type ``enum``.

For example, the component module of hello project created in `Getting Start <getstart.html>`__,
the directory hierarchy looks like:

.. parsed-literal::
    hello/
        component/              
            __init__.py
            hello.py
        server_config.yaml


In ``__init__.py``, it defines the subclass of ``ComponentTypes``. ``ComponentTypes`` is a customized subclass of `Eunm <https://docs.python.org/3/library/enum.html>`__ class. 
Its value is a ``tuple`` stores ``(key, package, class_or_function)`` for **hostray** maps 
the component configurations in ``server_config.yaml`` with the component classes should be imported. The code of ``__init__.py`` looks like:

.. code-block:: python

    from hostray.web.component import ComponentTypes

    class HelloComponentTypes(ComponentTypes):
        Hello = ('hello', 'hello', 'HelloComponent')


In ``hello.py``, it defines the ``HelloComponent`` inherits from ``Component`` class, the code looks like:

.. code-block:: python

    from hostray.web.component import Component
    from . import HelloComponentTypes

    class HelloComponent(Component):
        def init(self, component_manager, p1, *arugs, **kwargs) -> None:
            print('init Hello component load from', __package__, 'and the parameters p1:', p1)

        def hello(self):
            return 'Hello World, This is hostray generate hello component'

In ``server_config.yaml``, add the key **'hello'** under component block. That tells **hostray** load **HelloComponent** when starting api server:

.. code-block:: yaml

    # in server_config.yaml

    name: hostray Server
    port: 8888
    debug: False
    component:
        hello: 
            p1: 'This is p1'

Make Project's Modules Work
=======================================================

Briefly lists the things should be done for each reserved module:

* `controller <buildin.html#controllers>`__

    * Defines enums inherits from ``hostray.web.controller.ControllerType`` in ``__init__.py``
    * Implements the controller inherits `hostray build-in controllers <http://localhost:8888/buildin.html#controllers>`__ or directly use `tornado.web handlers <https://www.tornadoweb.org/en/stable/web.html>`__
    * Configres the controller block in ``server_config.yaml``

* `component <buildin.html#components>`__

    * Defines enums inherits from ``hostray.web.component.ComponentTypes`` in ``__init__.py``
    * Implements the component class inherits from `hostray.web.component.Component <web_refer.html#hostray.web.component.default_component.Component>`__
    * Configres the component block in ``server_config.yaml``

* `unit_test <buildin.html#unittest-cases>`__

    * Defines enums inherits from ``hostray.unit_test.UnitTestTypes`` in ``__init__.py``
    * Implements the test cases inherits from `hostray.unit_test.UnitTestCase <web_refer.html#hostray.unit_test.UnitTestCase>`__

Configuration Validator
=======================================================

**hostray** provides `configurations validator <web_refer.html#configuration-validator>`__ checks the build-in components and controllers. 
The validator is extendable to validate project extended components and controllers, and
the following example shows how to add validator of hello project's HelloComponent.

.. code-block:: python

    # in __init__.py of project's component module

    from hostray.web.component import ComponentTypes

    from hostray.web.config_validator import ConfigContainerMeta, ConfigElementMeta, HostrayWebConfigComponentValidator

    # add hello validator to component config validator
    HostrayWebConfigComponentValidator.set_cls_parameters(
        ConfigContainerMeta('hello', False,
            ConfigElementMeta('p1', str, True) # validate HelloComponent's 'p1' argument is required and string type
        )
    )

    class HelloComponentTypes(ComponentTypes):
        Hello = ('hello', 'hello', 'HelloComponent')
