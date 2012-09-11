#!/usr/bin/python
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

import argparse
import httplib2

from pivotal import pivotal
from pivotal.anyetree import etree

from corejet.core.model import Story
from corejet.core.parser import appendScenarios

from corejet.pivotal import config


def doPivotal(options, corejet_etree):

    try:
        pv = pivotal.Pivotal(options["token"], use_https=True)
    except TypeError:
        # Support HTTPS on pivotal_py == 0.1.3
        pivotal.BASE_URL = "https://www.pivotaltracker.com/services/v3/"
        pv = pivotal.Pivotal(options["token"])
    pivotal_project = pv.projects(options["project"])

    pivotal_story_etrees = {}

    def get_pivotal_story_etree(story_id):
        if story_id in pivotal_story_etrees:
            story_etree = pivotal_story_etrees[story_id]
        else:
            story_etree = pivotal_project.stories(story_id).get_etree()
            pivotal_story_etrees[story_id] = story_etree
        return pivotal_story_etrees[story_id]

    incomplete_tasks_xpath = "tasks/task[contains(complete/text(), 'false')]"

    for scenario in corejet_etree.findall(
            "story/scenario[@testStatus='pass']"):

        story_id = scenario.getparent().get("id")

        task = None
        # A fake story is needed to parse exact scenario names
        tmp = Story("id", "name")
        story_etree = get_pivotal_story_etree(story_id)
        for node in story_etree.xpath(incomplete_tasks_xpath):
            appendScenarios(tmp, node.findtext("description"))
            # Expect only one scenario per task
            if tmp.scenarios\
                    and tmp.scenarios[-1].name == scenario.get("name"):
                task = node

        if task is not None:
            print (u"Completed task #%s for "
                   u"https://www.pivotaltracker.com/story/show/%s") %\
                (task.findtext("position"), story_id)
            task.find("complete").text = "true"
            url = pivotal_project.stories(story_id)\
                                 .tasks(task.findtext("id")).url

            h = httplib2.Http(timeout=15)
            h.force_exception_to_status_code = True
            headers = {
                "X-TrackerToken": options["token"],
                "Content-Type": "application/xml"
            }
            h.request(url, "PUT", etree.tostring(task), headers=headers)
            if not story_etree.xpath(incomplete_tasks_xpath):
                print u"All tasks completed for #%s" % story_id

    for story in corejet_etree.findall("story"):
        # total_scenarios = len(story.findall("scenario"))
        passing_scenarios = story.findall("scenario[@testStatus='pass']")
        failing_scenarios = story.findall("scenario[@testStatus='fail']")
        pending_scenarios = story.findall("scenario[@testStatus='pending']")
        mismatch_scenarios = story.findall("scenario[@testStatus='mismatch']")

        if passing_scenarios and not (failing_scenarios or pending_scenarios
                                      or mismatch_scenarios):
            if story.get("requirementStatus") not in ["finished", "accepted",
                                                      "rejected", "delivered"]:
                status = u"COMMIT"
            else:
                status = u"OK"

        elif (mismatch_scenarios or pending_scenarios) and story.get(
                "requirementStatus") in\
                ["finished", "accepted", "rejected", "delivered"]:
            status = "REGRESSION"
        elif mismatch_scenarios or pending_scenarios:
            status = "UNSYNC"
        else:
            status = "FAIL"

        print ((u"#%s: passing %02d failing %02d outdated %02d "
                u"missing %02d status %s") %
               (story.get("id"), len(passing_scenarios),
                len(failing_scenarios), len(mismatch_scenarios),
                len(pending_scenarios), status)
               ).replace("00", "--")

        for scenario in pending_scenarios:
            print u"#%s: MISSING: Scenario: %s" %\
                (story.get("id"), scenario.get("name"))

        for scenario in mismatch_scenarios:
            story = scenario.getparent()
            print u"#%s: OUTDATED: \"Scenario: %s\"" %\
                (story.get("id"), scenario.get("name"))

        if mismatch_scenarios or pending_scenarios:
            print u"#%s: URI: https://www.pivotaltracker.com/story/show/%s" %\
                (story.get("id"), story.get("id"))


def __main__():
    parser = argparse.ArgumentParser(
        description=u"Check CoreJet report against PivotalTracker")
    parser.add_argument(
        "sections", nargs="?",
        help=(u"comma separated list of pivotal.cfg section names to "
              u"retrieve epics from"))
    parser.add_argument(
        "--token",
        help=u"default pivotal token to use to authenticate")
    parser.add_argument(
        "--project",
        help=u"default pivotal project id to retrieve stories from")
    parser.add_argument(
        metavar="corejet.xml", dest="filename", nargs="?",
        default="parts/test/corejet/corejet.xml",
        help=(u"path to CoreJet test report "
              u"(defaults to parts/test/corejet/corejet.xml)"))

    args = parser.parse_args()

    defaults = {
        "project": args.project,
        "token": args.token
    }
    defaults = config.read("defaults", defaults)

    sections = None
    if args.sections:
        sections = [name.strip() for name in args.sections.split(",")]
    if not sections and "epics" in defaults:
        sections = [name.strip() for name in defaults["epics"].split(",")]

    epics = {}
    if sections:
        for section in sections:
            epics[section] = config.read(section, defaults)

    if None in defaults.values():
        parser = argparse.ArgumentParser(
            description=u"Check CoreJet report against PivotalTracker")
        parser.add_argument(
            "--token", required=True,
            help=u"pivotal token to use to authenticate")
        parser.add_argument(
            "--project", required=True,
            help=u"pivotal project id to retrieve stories from")
        parser.add_argument(
            metavar="parts/test/corejet/corejet.xml", dest="filename",
            help=u"path to CoreJet test report")
        args = parser.parse_args()

    corejet_etree = etree.fromstring(open(args.filename).read())
    if not sections:
        for epic in corejet_etree.findall("epic"):
            doPivotal(defaults, epic)
    for epic in epics:
        doPivotal(epics[epic], corejet_etree.find("epic[@id='%s']" % epic))
