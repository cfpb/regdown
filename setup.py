from setuptools import find_packages, setup


with open("README.md") as f:
    long_description = f.read()


install_requires = [
    "Markdown>=3.2,<3.5",
]


testing_extras = [
    "coverage>=3.7.0",
]


setup(
    name="regdown",
    url="https://github.com/cfpb/regdown",
    author="CFPB",
    author_email="tech@cfpb.gov",
    description="Markdown extension for interactive regulations",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="CC0",
    version="1.0.5",
    include_package_data=True,
    packages=find_packages(),
    test_suite="regdown.tests",
    install_requires=install_requires,
    extras_require={
        "testing": testing_extras,
    },
    classifiers=[
        "License :: CC0 1.0 Universal (CC0 1.0) Public Domain Dedication",
        "License :: Public Domain",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
    ],
)
