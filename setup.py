from setuptools import setup

setup(
    name = 'Sophies Kitchen Knightmare',
    version = 1.0,
    description = 'Restaurant Simulator',
    author = 'Matt Law',
    author_email = 'mvl@cornell.edu',
    packages = ['sknightmare'],
    install_requires=['simpy', 'RandomWords', 'arrow', 'numpy', 'scipy'])
