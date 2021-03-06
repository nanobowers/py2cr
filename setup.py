"""
A code translator using AST from Python to Crystal.
This is basically a NodeVisitor with Crystal output.
See:
https://docs.python.org/3/library/ast.html
"""

from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()
    
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='py2cr',
    version='0.1.0',
    description='A code translator using AST from Python to Crystal',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/nanobowers/py2cr',
    author='Ben Bowers',
    author_email='nanobowers@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    keywords='python crystal',
    packages=['py2cr'],
    package_data = {
        'py2cr': ['modules/lib.yaml',
                  'modules/numpy.yaml',
                  'modules/unittest.yaml',
                  'builtins/require.cr',
                  'builtins/module.cr', ]
    },
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'py2cr=py2cr:main'
        ]
    }
)
