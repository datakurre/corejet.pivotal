CoreJet test runner Pivotal Tracker integration
===============================================

This package provides a requirements catalogue source for `corejet.testrunner`_
that can fetch requirements from Pivotal Tracker.

To use it, make sure it is installed in the working set of the testrunner. If
using Buildout, you can do this with::

    [test]
    recipe = corejet.testrunner
    eggs =
        corejet.pivotal
        <other packages>
    defaults = ['--auto-color', '--auto-progress']

Here is an example command line invocation::

  ./bin/test -s corejet.core --corejet="pivotal,token=mypivotaltoken,project=123456,filter=myepickeyword"

The ``--corejet`` option must start with ``pivotal,`` followed by a set of
parameters that indicate how to connect to Pivotal Tracker. The parameters are:

``token=<token>``
    `Pivotal token`_ to use to authenticate
``project=<project>``
    Pivotal project id to retrieve stories from
``filter=<filter>``
    `Pivotal filter`_ string to retrieve stories for this epic
``title=<title>``
    optional requirements catalog title (defaults to Pivotal project title)

Pivotal stories matching project and filter options may contain scenarios in
simple Gherkin syntax in their description field, e.g.::

  Scenario: First scenario
  Given a precondition
    And another precondition
  When something happens
    And something else happens
  Then a result is expected
    And another result is expected

  Scenario: Second scenario
  Given another precondition
  When something else happens
  Then a different result is expected

The parser is relatively forgiving, but note:

* The parser is case-insensitive
* Zero or more scenarios may be present
* Scenarios must start with "Scenario: " followed by a name
* The "Given" clause is optional, but must come first in a scenario
* The "When" clause is required, and must come before the "Then" clause
* The "Then"" clause is also required
* An "And" clause can come after any "Given", "When" or "Then", but not
  first.

Package `corejet.core`_ includes XSLT to generate test skeletons in Python from corejet.xml, e.g.::

  xsltproc eggs/corejet.core-1.0a4-py2.6.egg/corejet/core/xslt/corejet-to-python.xsl parts/test/corejet/corejet.xml

.. _corejet.core: http://pypi.python.org/pypi/corejet.core
.. _corejet.testrunner: http://pypi.python.org/pypi/corejet.testrunner
.. _Pivotal token: https://www.pivotaltracker.com/help/api?version=v2#retrieve_token
.. _Pivotal filter: https://www.pivotaltracker.com/help/api?version=v2#get_stories_by_filter
