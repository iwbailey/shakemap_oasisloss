"""
Installation of package
"""
import setuptools

# Get the long description from the readme
with open("README.md", "r") as fh:
    long_description = fh.read()

# All details
setuptools.setup(
    name='shakemap_oasisloss',
    version='0.0.1',
    url='',
    author='Iain Bailey',
    author_email='iainbailey@gmail.com',
    description='Use USGS shakemap to estimate earthquake loss from an event',
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT ",
        "Operating System :: OS Independent",
    ),
)
