import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='np_autodiscovery',
    version='1.0.0',
    packages=find_packages(),
    include_package_data=True,
    license='Apache 2.0',
    description='NetBox plugin which allows for auto discovery of existing devices in a network.',
    long_description=README,
    url='https://github.com/lampwins/np_autodiscovery/',
    author='John Anderson',
    author_email='lampwins@gmail.com',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 2.2',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: System :: Networking',
    ],
    install_requires=[
        'napalm',
        'django_rq',
    ]
)
