"""Install packages as defined in this file into the Python environment."""
from setuptools import setup, find_packages

# The version of this tool is based on the following steps:
# https://packaging.python.org/guides/single-sourcing-package-version/
VERSION = {}

with open("./unity_app_generator/version.py") as fp:
    # pylint: disable=W0122
    exec(fp.read(), VERSION)

setup(
    name="unity_app_generator",
   author="James McDuffie",
    url="https://github.com/unity-sds/unity-app-generator",
    description="Generates an OGC compliant Unity application package using the Unity app-pack-generator.",
    version=VERSION.get("__version__", "0.0.0"),
    packages=find_packages(where=".", exclude=["tests"]),
    include_package_data=True,
    package_data={"unity_app_generator": ["schemas/*", "templates/*"]},
    scripts=["build_ogc_app.py"],
    install_requires=[
        "app_pack_generator @ git+https://github.com/unity-sds/app-pack-generator.git",
        "unity-py @ git+https://github.com/unity-sds/unity-py.git@develop",
    ],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Programming Language :: Python :: 3.0",
        "Topic :: Utilities",
    ],
)
