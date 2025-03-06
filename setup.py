#!/usr/bin/env python3

import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    readme = fh.read()

from threefive3.version import version


setuptools.setup(
    name="threefive3",
    version=version,
    author="Adrian of Doom",
    author_email="spam@iodisco.com",
    description="SCTE-35 decoder and encoder with MPEGTS and HLS and XML support.",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/superkabuki/threefive3",
    install_requires=[
        "pyaes",
        "gums",
    ],

    scripts=['bin/threefive3'],
    packages=setuptools.find_packages(),
    classifiers=[
        "License :: OSI Approved :: Sleepycat License",
        "Environment :: Console",
        "Operating System :: OS Independent",
        "Operating System :: POSIX :: BSD :: OpenBSD",
        "Operating System :: POSIX :: BSD :: NetBSD",
        "Operating System :: POSIX :: Linux",
        "Topic :: Multimedia :: Video",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Programming Language :: Python :: Implementation :: CPython",
    ],
    python_requires=">=3.6",
)
