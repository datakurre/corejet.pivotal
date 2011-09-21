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


def pivotalSource(details):
    """Produce a CoreJet XML file with stories for a single epic from Pivotal.

    The parameter should be a comma-separated string with the following
    parameters:

    token=<token> - pivotal token to use to authenticate
    project=<project> - pivotal project id to retrieve stories from
    filter=<filter> - pivotal filter string to retrieve stories for this epic
    title=<title> - optional title for this epic
    """

    options = {}

    for option in details.split(","):
        key, value = option.split("=", 1)
        options[key.strip().lower()] = value.strip()

    assert options.get("token", False),\
           u"Pivotal token is a mandatory option."
    assert options.get("project", False),\
           u"Pivotal project id is a mandatory option."
    assert options.get("filter", False),\
           u"Pivotal filter string is a mandatory option."

    try:
        client = pivotal.Pivotal(options["token"], use_https=True)
    except TypeError:
        # Support HTTPS on pivotal_py == 0.1.3
        pivotal.BASE_URL = "https://www.pivotaltracker.com/services/v3/"
        client = pivotal.Pivotal(options["token"])

    project = client.projects(options["project"])
    stories = project.stories(filter=options["filter"])
    title = options.get("title", project.get_etree().findtext("name"))
    catalogue = RequirementsCatalogue(project=title,
                                      extractTime=datetime.now())

    for pivotal_story in stories.get_etree():
        story = Story(pivotal_story.findtext("id"),
                      pivotal_story.findtext("name"))
        story.status = pivotal_story.findtext("current_state")
        story.points = pivotal_story.findtext("estimate", None)
        if story.status in ["accepted", "rejected"]:
            story.resolution = story.status
        setBackground(story, pivotal_story.findtext("description"))
        for task in pivotal_story.find("tasks"):
            appendScenarios(story, task.findtext("description"))
        appendScenarios(story, pivotal_story.findtext("description"))
        if story.scenarios:
            epic = Epic(story.name, story.title)
            epic.stories.append(story)
            catalogue.epics.append(epic)

    return catalogue
