#!/usr/bin/env python
import setuptools
from distutils.util import convert_path

main_ns  = {};
ver_path = convert_path("tamu_met_products/version.py");
with open(ver_path) as ver_file:
    exec(ver_file.read(), main_ns);

setuptools.setup(
  name             = "tamu_met_products",
  description      = "For the TAMU HDWX Website",
  url              = "https://github.com/kms22134/tamu_met_products",
  author           = "Kevin Smalley, Kyle R. Wodzicki",
  author_email     = "ksmaley@tamu.edu,krwodzicki@gmail.com",
  version          = main_ns['__version__'],
  packages         = setuptools.find_packages(),
  install_requires = ['cartopy', 'matplotlib', 'metpy', 'pyproj', 'python-awips'],
  zip_safe         = False
);

