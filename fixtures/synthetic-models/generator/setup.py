import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="fault-tree-benchmark",
    version="0.0.1",
    author="",
    author_email="",
    description="Utility for benchmarking fault trees",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="git@gitlab.openpra.org:benchmarking/ft_solver.git",
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
    install_requires=['argparse', 'setuptools'],
    test_suite='nose.collector',
    tests_require=['nose', 'typing', 'argparse', 'coverage'],
)
