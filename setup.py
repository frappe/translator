from setuptools import setup, find_packages
import os

version = '0.0.1'

setup(
    name='translator',
    version=version,
    description='Translation Portal for Frappe Apps',
    author='Frappe Technologies',
    author_email='info@frappe.io',
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=("frappe",),
)
