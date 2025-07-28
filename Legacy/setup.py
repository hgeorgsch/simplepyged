from setuptools import setup, find_packages
from pyged import __version__

setup(
    name='pyged',
    version=__version__,
    description='A simple Python GEDCOM parser',
    long_description=open('README.rst', 'r').read(),
    keywords='gedcom, genealogy',
    author=u'Hans Georg Schaathun',
    author_email='hg+slekt@schaathun.net',
    url='https://github.com/hgeorgsch/pyged/',
    license='GPL',
    package_dir={'pyged': 'src/pyged'},
    include_package_data=True,
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Sociology :: Genealogy",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    zip_safe=False,
)

