version 0.2.0
# Snips Skill Roku

[![Latest Version](https://img.shields.io/pypi/v/snipsroku.svg)](https://pypi.python.org/pypi/snipsroku/)
[![Build Status](https://travis-ci.org/snipsco/snips-skill-roku.svg)](https://travis-ci.org/snipsco/snips-skill-roku)
[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](https://raw.githubusercontent.com/snipsco/snips-skill-roku/master/LICENSE.txt)

Note: Roku Search is only available in English, and only available for registered accounts in the U.S., Canada (English only), Ireland and the U.K


## Snips Manager

It is recommended that you use this skill with the [snips skill server]().

## Usage

The skill allows you to control [Roku](https://www.roku.com/) TV. You can use it as follows:
 - Go to home screen
 - Get dict with installed apps and apps id
 - Launch a specifc app already installed
 - Search for content
 - Launch a specific series or movie. For instance, Black Mirror season 4

### Configuration

The `ROKU_DEVICE_IP` is used to identify your Roku device in the network. You can either obtain the IP through the Roku interface
if you navigate to **Settings > Network > About** and note down what is next to "IP address". Alternatively, please follow the instructions
 [here](https://sdkdocs.roku.com/display/sdkdoc/External+Control+API#ExternalControlAPI-SSDP(SimpleServiceDiscoveryProtocol)).
If this configuration is not set, the app will search your network for a Roku devices.

## Contributing

Please see the [Contribution Guidelines](https://github.com/snipsco/snips-skill-roku/blob/master/CONTRIBUTING.md).

## Copyright

This skill is provided by [Snips](https://www.snips.ai) as Open Source software. See [LICENSE.txt](https://github.com/snipsco/snips-skill-roku/blob/master/LICENSE.txt) for more
information.
