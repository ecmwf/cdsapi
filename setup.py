#!/usr/bin/env python3
#

import io
import os.path

import setuptools


def read(fname):
    file_path = os.path.join(os.path.dirname(__file__), fname)
    return io.open(file_path, encoding='utf-8').read()


version = '0.0.1'


setuptools.setup(
    name='cdsapi',
    version=version,
    author='ECMWF',
    author_email='software@ecmwf.int',
    license='Apache 2.0',
    url='https://software.ecmwf.int/stash/projects/CST/repos/cdsapi',
    description="Climate Data Store API",
    long_description=read('README.rst'),
    packages=setuptools.find_packages(),
    include_package_data=True,
    setup_requires=[
        'pytest-runner',
    ],
    install_requires=[
        'requests',
    ],
    tests_require=[
        'pytest',
    ],
    zip_safe=True,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Operating System :: OS Independent',
    ],
)
