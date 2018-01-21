#!/usr/bin/env python3

import sys
from setuptools import setup
from setuptools import find_packages


if sys.version_info[:3] < (3, 3):
    raise SystemExit("You need Python 3.3+")


setup(
    name="bmii",
    version="0.1",
    description="",
    long_description=open("README.md").read(),
    author="Pierre Surply",
    author_email="pierre.surply@lse.epita.fr",
    install_requires=open('requirements.txt').readlines(),
    packages=find_packages(),
    package_data={
        "bmii.usbctl": [
            "3rdparty/*",
            "3rdparty/ixo-usb-jtag/*",
            "3rdparty/ixo-usb-jtag/fx2/*",
            "fw/*",
            "utils/99-bmii.rules"
        ]
    },
    entry_points={
          'console_scripts': [
              'bmii = bmii.__main__:main'
          ]
    },
    license="BSD",
    platforms=["Any"],
    keywords="",
    classifiers=[
        "Topic :: Scientific/Engineering :: Electronic Design Automation (EDA)",
        "Environment :: Console",
        "Development Status :: Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
    ],
)
