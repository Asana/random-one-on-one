import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="oneonone",
    packages=["oneonone"],
    version="0.0.1",
    author="Asana Inc",
    license="MIT",
    description="",
    long_description=long_description,
    long_description_content_type="text/markdown",
    python_requires=">=3.6",
    install_requires=["asana"],
    test_suite="tests",
)