# -*- coding: utf-8 -*-
# Copyright (c) 2011 University of Jyväskylä
#
# Authors:
#     Asko Soukka <asko.soukka@iki.fi>
#
# This file is part of corejet.pivotal.
#
# corejet.pivotal is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# corejet.pivotal is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with corejet.pivotal.  If not, see <http://www.gnu.org/licenses/>.

try:
    # Enable httplib2 to fetch urls under when under GAE SDK buildout
    from google.appengine.api import apiproxy_stub_map
    from google.appengine.api import urlfetch_stub
    # Create a stub map so we can build App Engine mock stubs.
    apiproxy_stub_map.apiproxy = apiproxy_stub_map.APIProxyStubMap()
    # Register App Engine mock stubs.
    apiproxy_stub_map.apiproxy.RegisterStub(
        "urlfetch", urlfetch_stub.URLFetchServiceStub())
except ImportError:
    pass

from datetime import datetime

from pivotal import pivotal

from corejet.core.model import RequirementsCatalogue, Epic, Story
from corejet.core.parser import appendScenarios

from corejet.pivotal import config


def appendScenariosFromPivotalStory(story, node, options):
    """Appends scenarios from Pivotal node or prints error"""
    try:
        appendScenarios(story, node.findtext("description") or u"",
                        default_language=options.get("language", "en"))

        for task in node.findall("tasks/task"):
            appendScenarios(story, task.findtext("description") or u"",
                            default_language=options.get("language", "en"))
    except ValueError, e:
        print("Could not parse story %s\n%s" % (node.findtext("url"), str(e)))


def pivotalSource(details):
    """Produce a CoreJet XML file with stories for epics from Pivotal.

    The parameter should be a comma-separated string with the following
    parameters:

    <epic>,<epic>,... - optional cfg section names to retrieve options per epic
    token=<token> - default pivotal token to use in authentication
    project=<project> - default pivotal project id to retrieve stories from
    filter=<filter> - default pivotal filter string to retrieve stories
    title=<title> - optional title for the requirements catalog
                    (defaults to the first found pivotal project title)
    """

    sections = []
    defaults = {}

    for option in details.split(","):
        try:
            key, value = option.split("=", 1)
        except ValueError:
            # values without keys are interpreted as cfg-sections
            value = option.strip()
            if value:
                sections.append(value)
            continue
        defaults[key.strip().lower()] = value.strip()

    defaults = config.read("defaults", defaults)

    if not sections and "epics" in defaults:
        sections = [name.strip() for name in defaults["epics"].split(",")]

    if not sections:
        sections = ["defaults"]

    epics = []

    for section in sections:
        options = config.read(section, defaults)

        assert options.get("token", False),\
            u"Pivotal token is a mandatory option."
        assert options.get("project", False),\
            u"Pivotal project id is a mandatory option."
        assert options.get("filter", False),\
            u"Pivotal filter string is a mandatory option."

        # append filter from command line (when found)
        if defaults.get("filter", "") not in options["filter"]:
            options["filter"] += " %s" % defaults["filter"]

        # set includedone:true if it's not explicitly set otherwise
        if not "includedone:" in options["filter"]:
            options["filter"] += " includedone:true"

        try:
            pv = pivotal.Pivotal(options["token"], use_https=True)
        except TypeError:
            # Support HTTPS on pivotal_py == 0.1.3
            pivotal.BASE_URL = "https://www.pivotaltracker.com/services/v3/"
            pv = pivotal.Pivotal(options["token"])

        project = pv.projects(options["project"])
        project_etree = project.get_etree()
        project_title =\
            options.get("title", project_etree.findtext("name"))
        if not type(project_title) == unicode:  # ensure unicode
            project_title = unicode(project_title, "utf-8", "ignore")

        if not "title" in defaults:
            defaults["title"] = project_title

        epic_title = options.get("title", project_title)
        if not type(epic_title) == unicode:  # ensure unicode
            epic_title = unicode(epic_title, "utf-8", "ignore")

        epic = Epic(name=section != "defaults" and section
                    or str(sections.index(section) + 1),
                    title=epic_title)

        stories = project.stories(filter=options["filter"])
        stories_etree = stories.get_etree()

        for node in stories_etree:
            story = Story(node.findtext("id"), node.findtext("name"))
            story.status = node.findtext("current_state")
            if story.status in ["accepted", "rejected"]:
                story.resolution = story.status
            story.points = node.findtext("estimate", None)

            appendScenariosFromPivotalStory(story, node, options)

            if story.scenarios:
                epic.stories.append(story)
        epics.append(epic)

    catalogue = RequirementsCatalogue(project=defaults["title"],
                                      extractTime=datetime.now())
    for epic in epics:
        catalogue.epics.append(epic)

    return catalogue
