from setuptools import setup, find_packages

__version__ = "1.0"

with open("turboseti_stream/version.py", "w") as fh:
    fh.write("TURBOSETI_STREAM_VERSION = '{}'\n".format(__version__))

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("requirements.txt", "r") as fh:
    install_requires = fh.readlines()

with open("requirements_test.txt", "r") as fh:
    test_requirements = fh.readlines()

entry_points = {
    'console_scripts' :  []
}

package_data={
    'turboseti_stream': []
}

setup(
    name="turboseti_stream",
    version=__version__,
    packages=find_packages(),
    package_data=package_data,
    include_package_data=True,
    install_requires=install_requires,
    tests_require=test_requirements,
    entry_points=entry_points,
    author="Seti Breakthrough Listen",
    description="Streaming data front-end to turbo_seti",
    long_description=long_description,
    long_description_content_type='text/markdown',
    license="MIT License",
    keywords="astronomy",
    url="https://github.com/UCBerkeleySETI/turboseti_stream",
    zip_safe=False,
    options={"bdist_wheel": {"universal": "1"}},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3",
        "Topic :: Scientific/Engineering",
        ]
)
