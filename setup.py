import sys

from setuptools import find_packages, setup

if sys.version_info < (3, 0):
    sys.exit("Sorry, Python < 3.0 is not supported")

import re

VERSIONFILE = "xferprod/_version.py"
verstrline = open(VERSIONFILE, "rt").read()
VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"
mo = re.search(VSRE, verstrline, re.M)
if mo:
    verstr = mo.group(1)
else:
    raise RuntimeError("Unable to find version string in %s." % (VERSIONFILE,))

entry_points = {
    'console_scripts': [
        "xferprod = xferprod.main:main",
    ],
}

install_requires = [
    "argcomplete >= 1.8.2",
    "colorama >= 0.3.7",
]

setup(
    name="xferprod",
    version=verstr,
    description="xferprod",
    long_description="Please visit `Github <https://github.com/saycv/xferprod>`_ for more information.",
    author="xferprod project developers",
    author_email="",
    url="https://github.com/saycv/xferprod",
    packages=find_packages(exclude=["tests", "*.tests", "*.tests.*", "tests.*"]),
    entry_points=entry_points,
    include_package_data=True,
    install_requires=install_requires,
)
