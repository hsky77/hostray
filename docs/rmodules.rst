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
    :linenos:

    from hostray.web.component import ComponentTypes

    class HelloComponentTypes(ComponentTypes):
        Hello = ('hello', 'hello', 'HelloComponent')


In ``hello.py``, it defines the ``HelloComponent`` inherits from ``Component`` class, the code looks like:

.. code-block:: python
    :linenos:

    from hostray.web.component import Component

    class HelloComponent(Component):
        def init(self, component_manager, *arugs, **kwargs) -> None:
            print('init HelloComponent from', __package__)


In ``server_config.yaml``, add the key **'hello'** under component block. That tells **hostray** load **HelloComponent** when starting api server:

.. code-block:: yaml
    :linenos:

    # in server_config.yaml

    name: Hostray Server
    port: 8888
    debug: False
    component:
        hello: # add this key

Make Project's Modules Work
=======================================================

Briefly lists the things should be done for each reserved module:

`controller <refer.html#controllers>`__
    * defines enums inherits from ``hostray.web.controller.ControllerType`` in ``__init__.py``
    * implements the controller inherits or directly use `tornado.web handlers <https://www.tornadoweb.org/en/stable/web.html>`__ or hostray build-in controllers
    * configres the controller block in ``server_config.yaml``
`component <refer.html#components>`__
    * defines enums inherits from ``hostray.web.component.ComponentTypes`` in ``__init__.py``
    * implements the component class inherits from ``hostray.web.component.Component``
    * configres the component block in ``server_config.yaml``
`unit_test <refer.html#unittest-cases>`__
    * defines enums inherits from ``hostray.unit_test.UnitTestTypes`` in ``__init__.py``
    * implements the test cases inherits from ``hostray.unit_test.UnitTestCase``

Configuration Validator
=======================================================

It is great if the server configurations could be validated and told the configred mistakes. 
**hostray** provide the `configurations validator <refer.html#configuration-validator>`__ checks the build-in components and controllers. The validator is also extendable.
The following example shows how to add validator of hello project's HelloComponent.

.. code-block:: python
    :linenos:

    from hostray.web.component import ComponentTypes

    from hostray.web.config_validator import ConfigContainerMeta, ConfigElementMeta, HostrayWebConfigComponentValidator

    # add hello validator to component config validator
    HostrayWebConfigComponentValidator.set_cls_parameters(
        ConfigContainerMeta('hello', False,
            # ConfigElementMeta('p1', str, True) # marked, so validator does not validate HelloComponent's 'p1' argument
        )
    )

    class UTServerComponentTypes(ComponentTypes):
        Hello = ('hello', 'hello', 'HelloComponent')

:class hostray.web.config_validator.ConfigBaseElementMeta:

    base config element metaclass

    :set_cls_parameters(\*cls_parameters) -> None:

        set the sub class elements
    
    :get_cls_parameter(key_routes, delimeter=".") -> type:

        get the sub class elements

:class hostray.web.config_validator.HostrayWebConfigValidator:

    default validator to validate `server_config.yaml` inherits from ConfigBaseElementMeta.

:class hostray.web.config_validator.HostrayWebConfigControllerValidator:

    default validator to validate the controller block of ``server_config.yaml`` inherits from ConfigBaseElementMeta.

:class hostray.web.config_validator.HostrayWebConfigComponentValidator:

    default validator to validate the component block of ``server_config.yaml`` inherits from ConfigBaseElementMeta.

:class hostray.web.config_validator.ConfigContainerMeta:

    config validation element metaclass contain sub elements

:class hostray.web.config_validator.ConfigElementMeta:

    config validation element metaclass store parameters

:class hostray.web.config_validator.ConfigScalableContainerMeta:

    scalable config validation element metaclass contain sub elements metaclass

:class hostray.web.config_validator.ConfigScalableElementMeta:

    scalable config validation element metaclass

:class hostray.web.config_validator.ConfigSwitchableElementMeta:

    switchable config validation element metaclass