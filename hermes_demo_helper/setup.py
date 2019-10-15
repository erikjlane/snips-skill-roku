from setuptools import setup

setup(
    name='hermes_demo_helper',
    version='0.0.1',
    description='wrapper for snips Demo',
    author='Snips',
    author_email='bjay.kamwa-watanabe@snips.ai',
    url='',
    download_url='',
    license='MIT',
    install_requires=[
       'hermes_python'
    ],
    test_suite="tests",
    keywords=['snips'],
    packages=[
        'hermes_demo_helper'
    ],
    include_package_data=True,
)
