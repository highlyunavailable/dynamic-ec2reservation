""" Setup script for PyPI """
import os
from setuptools import setup
from ConfigParser import SafeConfigParser

settings = SafeConfigParser()
settings.read(os.path.realpath('dynamic_ec2reservation/dynamic-ec2reservation.conf'))


setup(
    name='dynamic-ec2reservation',
    version=settings.get('general', 'version'),
    license='Apache License, Version 2.0',
    description='Automatic rebalancing of AWS EC2 Reserved Instances between Availability Zones',
    author='Tiru Srikantha',
    author_email='tiru.srikantha@gmail.com',
    url='https://github.com/highlyunavailable/dynamic-ec2reservation',
    keywords="ec2 aws reservations amazon web services",
    platforms=['Any'],
    packages=['dynamic_ec2reservation'],
    scripts=['dynamic-ec2reservation'],
    include_package_data=True,
    zip_safe=True,
    install_requires=[
        'boto >= 2.29.1'
    ],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Console',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python'
    ]
)
