from setuptools import setup, find_packages

setup(
    name="corejet.pivotal",
    version="1.1.0",
    description="Pivotal Tracker data source for corejet.testrunner",
    long_description=(open("README.rst").read() + "\n" +
                      open("CHANGES.txt").read()),
    # Get more strings from
    # http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Programming Language :: Python",
    ],
    keywords="corejet pivotal",
    author="Asko Soukka",
    author_email="asko.soukka@iki.fi",
    url="https://github.com/datakurre/corejet.pivotal/",
    license="GPL",
    packages=find_packages(exclude=["ez_setup"]),
    namespace_packages=["corejet"],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "setuptools",
        # -*- Other dependencies: -*-
        "corejet.core",
        "argparse",
        "pivotal-py",
    ],
    entry_points="""
    # -*- Entry points: -*-
    [corejet.repositorysource]
    pivotal = corejet.pivotal:pivotalSource
    [console_scripts]
    pivotal = corejet.pivotal.tool:__main__
    """,
)
