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


In ``__init__.py``, it defines the subclass of ``ComponentTypes``. ``ComponentTypes`` is a customized subclass of ``Eunm`` class. 
Its value is a ``tuple`` stores (**key**, **package**, **class_or_function**) for **hostray** server maps 
the component configurations in ``server_config.yaml`` with the components should be imported. The code of ``__init__.py`` looks like:

.. code-block:: python

    from hostray.web.component import ComponentTypes

    class HelloComponentTypes(ComponentTypes):
        Hello = ('hello', 'hello', 'HelloComponent')


In ``hello.py``, it defines the ``HelloComponent`` inherits from ``Component`` class, the code looks like:

.. code-block:: python

    from hostray.web.component import Component

    class HelloController(RequestController):
        async def get(self):
            hello_comp = self.component_manager.get_component(HelloComponentTypes.Hello)
            self.write(hello_comp.hello())


In ``server_config.yaml``, add the key **'hello'** under component block. That tells **hostray** load **HelloComponent** when starting api server:

.. code-block:: yaml

    # in server_config.yaml

    name: Hostray Server
    port: 8888
    debug: False
    component:
        hello: # add this key

Make Project's Modules Work
=======================================================

Briefly lists the things should be done for each reserved module:

* `controller <buildin.html#controllers>`__

    * defines enums inherits from ``hostray.web.controller.ControllerType`` in ``__init__.py``
    * implements the controller inherits/directly use `tornado.web handlers <https://www.tornadoweb.org/en/stable/web.html>`__ or `hostray build-in controllers <http://localhost:8888/buildin.html#controllers>`__
    * configres the controller block in ``server_config.yaml``

* `component <buildin.html#components>`__

    * defines enums inherits from ``hostray.web.component.ComponentTypes`` in ``__init__.py``
    * implements the component class inherits from `hostray.web.component.Component <web_refer.html#hostray.web.component.default_component.Component>`__
    * configres the component block in ``server_config.yaml``

* `unit_test <buildin.html#unittest-cases>`__

    * defines enums inherits from ``hostray.unit_test.UnitTestTypes`` in ``__init__.py``
    * implements the test cases inherits from `hostray.unit_test.UnitTestCase <web_refer.html#hostray.unit_test.UnitTestCase>`__

Configuration Validator
=======================================================

**hostray** provides `configurations validator <web_refer.html#configuration-validator>`__ checks the build-in components and controllers. 
The validator is extendable to validate project extended components and controllers, and
the following example shows how to add validator of hello project's HelloComponent.

.. code-block:: python

    from hostray.web.component import ComponentTypes

    from hostray.web.config_validator import ConfigContainerMeta, ConfigElementMeta, HostrayWebConfigComponentValidator

    # add hello validator to component config validator
    HostrayWebConfigComponentValidator.set_cls_parameters(
        ConfigContainerMeta('hello', False,
            # ConfigElementMeta('p1', str, True) # validate HelloComponent's 'p1' argument is required and string type
        )
    )

    class HelloComponentTypes(ComponentTypes):
        Hello = ('hello', 'hello', 'HelloComponent')
