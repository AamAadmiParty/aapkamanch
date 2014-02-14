from setuptools import setup, find_packages
import os

version = '0.0.1'

setup(
    name='aapkamanch',
    version=version,
    description='Portal for Aam Aadmi Party',
    author='Contributors',
    author_email='rmehta@gmail.com',
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=("frappe",),
)
