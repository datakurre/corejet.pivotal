CoreJet test runner Pivotal Tracker integration
===============================================

This package provides a requirements catalogue source for `corejet.testrunner`_
that can fetch requirements from Pivotal Tracker.

To use it, make sure it is installed in the working set of the testrunner. If
using Buildout, you can do this with::

    [test]
    recipe = corejet.recipe.testrunner
    eggs =
        corejet.pivotal
        <other packages>
    defaults = ['--auto-color', '--auto-progress']

Here is an example command line invocation::

  ./bin/test -s corejet.core --corejet="pivotal,token=mypivotaltoken,project=123456,filter=myepickeyword"

The ``--corejet`` option must start with ``pivotal,`` followed by a set of
parameters that indicate how to connect to Pivotal Tracker. The parameters are:

``<epic>,<epic>,...``
    optional pivotal.cfg section names to retrieve options per epic
``token=<token>``
    default `Pivotal token`_ to use in authentication
``project=<project>``
    default Pivotal project id to retrieve stories from
``filter=<filter>``
    default `Pivotal filter`_ string to retrieve stories for this epic
``title=<title>``
    optional requirements catalog title (defaults to the first found Pivotal
    project title)

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
* An "And" or "But" clause can come after any "Given", "When" or "Then", but
  not first.

Please, note that ``filter`` will include ``includedone:true`` implicitly when
it's not explicitly set to *false*.

Optional ``pivotal.cfg`` which is looked at first the current working directory
upwards (or from ``~/.pivotalrc``) may be an INI-style config file describing
key value pairs within sections (special ``defaults``-section is supported for
defining defaults).

You may define several epics, for example, with the following setup:

1) ``~/.pivotalrc``::

     [defaults]
     token = mysecretpivotaltrackertoken

2) ``./pivotal.cfg``::

     [defaults]
     title = My project
     project = 123456

     [first-epic]
     title = A component for my project
     filter = label:firstlabel

     [another-epic]
     title = An another component for my project
     filter = label:anotherlabel

3) Execute CoreJet with::

     ./bin/test  --corejet="pivotal,first-epic,another-epic"

It's also possible to define list of epic-sections in ``[defaults]`` with
``epics = first-epic,another-epic`` and run tests with ``--corejet=pivotal``.

Package `corejet.core`_ includes XSLT to generate test skeletons in Python from
corejet.xml, e.g.::

  xsltproc eggs/corejet.core-1.0.0-py2.6.egg/corejet/core/xslt/corejet-to-python.xsl parts/test/corejet/corejet.xml

Install experimental ``bin/pivotal`` tool by adding the following part into
your ``buildout.cfg``::

  [buildout]
  parts += scripts

  [scripts]
  recipe = zc.recipe.egg
  eggs = corejet.pivotal

.. _corejet.core: http://pypi.python.org/pypi/corejet.core
.. _corejet.testrunner: http://pypi.python.org/pypi/corejet.testrunner
.. _Pivotal token: https://www.pivotaltracker.com/help/api?version=v3#retrieve_token
.. _Pivotal filter: https://www.pivotaltracker.com/help#howcanasearchberefined
