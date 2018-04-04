
from setuptools import setup

setup(
    name='snipsroku',
    version='0.1.0',
    description='Roku skill for Snips',
    author='Snips Labs',
    author_email='support@snips.ai',
    license='MIT',
    install_requires=['requests', 'mock'],
    keywords=['snips', 'roku'],
    packages=['snipsroku'],
    package_data={'snipsroku': ['Snipsspec']},
    include_package_data=True,
)
