#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = ['Click>=7.0', ]

test_requirements = [ ]

setup(
    author="Benjamin Herro",
    author_email='benjamincsherro@gmail.com',
    python_requires='>=3.7',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
    description="A leaky bucket implemented in python with a variety of persistence options if required",
    install_requires=requirements,
    license="MIT license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='leaky_bucket_limiter',
    name='leaky_bucket_limiter',
    packages=find_packages(include=['leaky_bucket_limiter', 'leaky_bucket_limiter.*']),
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/duneraccoon/leaky_bucket_limiter',
    version='0.1.0',
    zip_safe=False,
)
