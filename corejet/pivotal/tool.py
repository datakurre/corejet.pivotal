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
    project = pv.projects(options["project"])

    incomplete_tasks = "tasks/task[contains(complete/text(), 'false')]"

    stories = {}
    for scenario in corejet_etree.xpath("//scenario[@testStatus='pass']"):

        story_id = scenario.getparent().get("id")
        if story_id in stories:
            story_etree = stories[story_id]
        else:
            story_etree = project.stories(story_id).get_etree()
            stories[story_id] = story_etree

        task = None
        # A fake story is needed to parse exact scenario names
        tmp = Story("id", "name")

        for node in story_etree.xpath(incomplete_tasks):
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
            url = project.stories(story_id)\
                         .tasks(task.findtext("id")).url

            h = httplib2.Http(timeout=15)
            h.force_exception_to_status_code = True
            headers = {
                "X-TrackerToken": options["token"],
                "Content-Type": "application/xml"
                }
            h.request(url, "PUT", etree.tostring(task), headers=headers)
            if not story_etree.xpath(incomplete_tasks):
                print u"All tasks completed for #%s" % story_id


def __main__():
    parser = argparse.ArgumentParser(
        description=u"Check CoreJet report against PivotalTracker")
    parser.add_argument(
        "section", nargs="?",
        help=u"pivotal.cfg section name to retrieve arguments from")
    parser.add_argument(
        "--token",
        help=u"pivotal token to use to authenticate")
    parser.add_argument(
        "--project",
        help=u"pivotal.cfg section name to retrieve arguments from")
    parser.add_argument(
        metavar="corejet.xml", dest="filename",
        help=u"path to CoreJet test report")

    args = parser.parse_args()

    options = {
        "project": args.project,
        "token": args.token
        }

    options = config.read(args.section, options)

    if None in options.values():
        parser = argparse.ArgumentParser(
            description=u"Check CoreJet report against PivotalTracker")
        parser.add_argument(
            "--token", required=True,
            help=u"pivotal token to use to authenticate")
        parser.add_argument(
            "--project", required=True,
            help=u"pivotal.cfg section name to retrieve arguments from")
        parser.add_argument(
            metavar="parts/test/corejet/corejet.xml", dest="filename",
            help=u"path to CoreJet test report")
        args = parser.parse_args()

    corejet_etree = etree.fromstring(open(args.filename).read())
    return doPivotal(options, corejet_etree)
