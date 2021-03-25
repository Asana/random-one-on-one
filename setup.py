import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="asana_random_one_on_one",
    packages=["asana_random_one_on_one"],
    version="0.0.1",
    author="Asana Inc",
    license="MIT",
    description="",
    long_description=long_description,
    long_description_content_type="text/markdown",
    python_requires=">=3.6",
    install_requires=["asana>=0.10.1"],
    test_suite="tests",
)
