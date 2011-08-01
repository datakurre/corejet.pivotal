from setuptools import setup, find_packages

version = "1.0"

setup(name="corejet.pivotal",
      version=version,
      description="Adds 'pivotal' repository source for corejet.testrunner.",
      long_description=open("README.rst").read() + "\n" +
                       open("HISTORY.txt").read(),
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords="corejet testrunner",
      author="Asko Soukka",
      author_email="asko.soukka@iki.fi",
      url="",
      license="GPL",
      packages=find_packages(exclude=["ez_setup"]),
      namespace_packages=["corejet"],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          "setuptools",
          # -*- Other dependencies: -*-
          "corejet.core",
          "pivotaltracker",
      ],
      entry_points="""
      # -*- Entry points: -*-
      [corejet.repositorysource]
      pivotal = corejet.pivotal:pivotalSource
      """,
      )
