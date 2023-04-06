from setuptools import find_packages, setup


def read_file(file_name: str) -> str:
    with open(file_name) as fo:
        return fo.read().strip()


setup(
    name="cloudshell-tc-scripts",
    url="http://www.qualisystems.com/",
    author="QualiSystems",
    author_email="info@qualisystems.com",
    packages=find_packages(),
    install_requires=[
        "pygithub~=1.54",
        "click~=8.0",
        "requests~=2.25",
        "pydantic~=1.7",
        "dohq-teamcity~=1.0.5",
        "teamcity-messages~=1.28",
    ],
    tests_require=read_file("test_requirements.txt"),
    python_requires="~=3.9",
    version=read_file("version.txt"),
    package_data={"": ["*.txt"]},
    include_package_data=True,
    entry_points={"console_scripts": ["tc = scripts.cli:cli"]},
    description="Cloudshell TC scripts",
    long_description="TC scripts for automation tests",
    long_description_content_type="text/x-rst",
)
