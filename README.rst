Sonos skill for Snips
=====================

|Build Status| |MIT License|

Snips Skills Manager
^^^^^^^^^^^^^^^^^^^^

It is recommended that you use this skill with the `Snips Skills Manager <https://github.com/snipsco/snipsskills>`_. Simply add the following section to your `Snipsfile <https://github.com/snipsco/snipsskills/wiki/The-Snipsfile>`_:

.. code-block:: yaml

  skills:
    - pip: https://github.com/snipsco/snips-skills-roku
      package_name: snipsroku
      params:
        roku_device_ip: YOUR_ROKU_DEVICE_IP

Usage
-----

The skill allows you to control `Roku <https://www.roku.com/>`_ TV. You can use it as follows:

.. code-block:: python

    from snipsroku.snipsroku import SnipsRoku


    roku = SnipsRoku(ROKU_DEVICE_IP)
    # Go to home screen
    roku.home_screen()

    # Get dict with installed apps and apps id
    roku.get_apps()

    # Launch a specifc app already installed
    id = roku.get_app_id("Youtube")
    roku.launch_app(id)

    # Search for content
    roku.search_content("tv-show", "Friends")

    # Launch a specific series or movie. For instance, Black Mirror season 4
    roku.search_content("tv-show", "Black Mirror", None, True, "Netflix", 4)



The ``ROKU_DEVICE_IP`` is used to identify your Roku device in the network. You can either obtain the IP through the Roku interface
if you navigate to Settings > Network > About and note down what is next to "IP address". Or alternatively follow the instructions `here <https://sdkdocs.roku.com/display/sdkdoc/External+Control+API#ExternalControlAPI-SSDP(SimpleServiceDiscoveryProtocol)>`_

Copyright
---------

This skill is provided by `Snips <https://www.snips.ai>`_ as Open Source software. See `LICENSE.txt <https://github.com/snipsco/snips-skill-roku/blob/master/LICENSE.txt>`_ for more
information.

.. |Build Status| image:: https://travis-ci.org/snipsco/snips-skill-roku.svg
   :target: https://travis-ci.org/snipsco/snips-skill-roku
   :alt: Build Status
.. |MIT License| image:: https://img.shields.io/badge/license-MIT-blue.svg
   :target: https://raw.githubusercontent.com/snipsco/snips-skill-roku/master/LICENSE.txt
   :alt: MIT License
