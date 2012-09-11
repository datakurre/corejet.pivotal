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

import os

import ConfigParser


def read(section=None, defaults={}, filename=None):
    sep = os.path.sep
    parts = os.getcwd().split("/")

    if filename:
        basename = os.path.basename(filename)
        paths = [sep.join(parts) + sep + basename] +\
                [sep.join(parts[:-i]) + sep + basename
                 for i in range(1, len(parts))]
    else:
        paths = [sep.join(parts) + sep + "pivotal.cfg"] +\
                [sep.join(parts[:-i]) + sep + "pivotal.cfg"
                 for i in range(1, len(parts))] +\
                [os.path.expanduser("~" + sep + ".pivotalrc")]

    options = defaults.copy()

    for path in paths:

        if os.path.isfile(path):
            config = ConfigParser.ConfigParser()
            config.read(path)

            if not len(config.sections()):
                continue

            if section and not config.has_section(section):
                continue

            if not config.has_section("defaults"):
                continue

            section = section or "defaults"
            for key in config.options(section):
                # options in "defaults" section must not override existing
                if section != "defaults"\
                        or (key not in options or not options[key]):
                    options[key] = config.get(section, key)

            # "defaults"-sections are read from any cfg-file found
            if section != "defaults":
                return options

    return options
