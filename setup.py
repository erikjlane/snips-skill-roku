
from setuptools import setup

setup(
    name='snipssonos',
    version='1.0.0',
    description='Roku skill for Snips',
    author='The Als',
    license='MIT',
    install_requires=['requests'],
    keywords=['snips', 'roku'],
    packages=['snipsroku'],
    package_data={'snipsroku': ['Snipsspec']},
    include_package_data=True,
)