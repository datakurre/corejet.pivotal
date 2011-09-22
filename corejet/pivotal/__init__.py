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

from datetime import datetime

from pivotal import pivotal

from corejet.core.model import RequirementsCatalogue, Epic, Story
from corejet.core.parser import setBackground, appendScenarios

from corejet.pivotal import config


def pivotalSource(details):
    """Produce a CoreJet XML file with stories for a single epic from Pivotal.

    The parameter should be a comma-separated string with the following
    parameters:

    <section> - pivotal.cfg section name to retrieve missing arguments from
    token=<token> - pivotal token to use to authenticate
    project=<project> - pivotal project id to retrieve stories from
    filter=<filter> - pivotal filter string to retrieve stories for this epic
    title=<title> - optional title for this epic (defaults to project name)
    """

    options = {}

    for option in details.split(","):
        try:
            key, value = option.split("=", 1)
        except ValueError:
            # only value without key is allowed and that's "section"
            key = "section"
            value = option
        options[key.strip().lower()] = value.strip()

    options = config.read(options.get("section", None), options)

    assert options.get("token", False),\
           u"Pivotal token is a mandatory option."
    assert options.get("project", False),\
           u"Pivotal project id is a mandatory option."
    assert options.get("filter", False),\
           u"Pivotal filter string is a mandatory option."

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

    stories = project.stories(filter=options["filter"])
    stories_etree = stories.get_etree()

    title = options.get("title", project_etree.findtext("name"))
    catalogue = RequirementsCatalogue(project=title,
                                      extractTime=datetime.now())

    for node in stories_etree:
        story = Story(node.findtext("id"), node.findtext("name"))
        story.status = node.findtext("current_state")
        if story.status in ["accepted", "rejected"]:
            story.resolution = story.status
        story.points = node.findtext("estimate", None)

        setBackground(story, node.findtext("description"))

        for task in node.findall("tasks/task"):
            appendScenarios(story, task.findtext("description"))

        appendScenarios(story, node.findtext("description"))

        if story.scenarios:
            epic = Epic(story.name, story.title)
            epic.stories.append(story)
            catalogue.epics.append(epic)

    return catalogue
