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

import httplib2

from datetime import datetime

from pivotal import pivotal
from pivotal.anyetree import etree

from corejet.core.model import RequirementsCatalogue, Epic, Story, Scenario
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

    options = {
        "complete": True
        }

    for option in details.split(","):
        if option == "nocomplete":
            options["complete"] = False
            continue
        key, value = option.split("=", 1)
        options[key.strip().lower()] = value.strip()

    assert options.get("token", False),\
           u"Pivotal token is a mandatory option."
    assert options.get("project", False),\
           u"Pivotal project id is a mandatory option."
    assert options.get("filter", False),\
           u"Pivotal filter string is a mandatory option."

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

    def set_status(self, status):
        if status == "pass" and self.pv_options["complete"]:
            task = None
            # A fake story is needed to parse exact scenario names
            tmp = Story("id", "name")
            incomplete_tasks = "//task[contains(complete/text(), 'false')]"
            for node in self.pv_stories_etree.xpath(incomplete_tasks):
                appendScenarios(tmp, node.findtext("description"))
                # Expect only one scenario per task
                if tmp.scenarios and tmp.scenarios[-1].name == self.name:
                    task = node
            if task is not None:
                task.find("complete").text = "true"
                url = self.pv_project.stories(self.story.name)\
                                     .tasks(task.findtext("id")).url

                h = httplib2.Http(timeout=15)
                h.force_exception_to_status_code = True
                headers = {
                    "X-TrackerToken": self.pv_project.token,
                    "Content-Type": "application/xml"
                    }
                h.request(url, "PUT", etree.tostring(task), headers=headers)
        self._status = status

    def get_status(self):
        return getattr(self, "_status", None)

    # Monkeypatch Scenario to enable us reporting completed tasks
    Scenario.pv_options = options
    Scenario.pv_project = project
    Scenario.pv_stories_etree = stories_etree
    Scenario.status = property(get_status, set_status)

    for node in stories_etree:
        story = Story(node.findtext("id"), node.findtext("name"))
        story.status = node.findtext("current_state")
        if story.status in ["accepted", "rejected"]:
            story.resolution = story.status
        story.points = node.findtext("estimate", None)

        setBackground(story, node.findtext("description"))

        for task in node.find("tasks"):
            appendScenarios(story, task.findtext("description"))

        appendScenarios(story, node.findtext("description"))

        if story.scenarios:
            epic = Epic(story.name, story.title)
            epic.stories.append(story)
            catalogue.epics.append(epic)

    return catalogue
