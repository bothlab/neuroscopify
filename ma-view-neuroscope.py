#!/usr/bin/env python3
#!/usr/bin/env python3
#
# Copyright (C) 2012-2016 Matthias Klumpp <matthias@tenstral.net>
#
# Licensed under the GNU Lesser General Public License Version 3
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the license, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import sys
import argparse
import subprocess

from convert import convert_ma

def main():
    parser = argparse.ArgumentParser(description="Convert MazeAmaze data in a format Neuroscope can understand")
    parser.add_argument("--root", help="MazeAmaze data root path", type=str)
    parser.add_argument("--subject", help="Name of the test subject (mouse/rat)", type=str)
    parser.add_argument("--time", help="Time of the experiment", type=str)
    parser.add_argument("--experiment", help="Experiment name", type=str)
    parser.add_argument("--open", help="Open Neuroscope", action='store_true')
    parser.add_argument("--no-override-settings", help="Do not override Neuroscope settings", action='store_true')
    args = parser.parse_args()

    if not args.root:
        print("No root path given!")
        return 1
    if not args.subject:
        print("You need to set a subject name!")
        return 1
    if not args.time:
        print("No time is set for the given subject.")
        return 1
    if not args.experiment:
        print("No experiment-id is given!")
        return 1

    rdir = convert_ma(args.root, \
                      args.subject, \
                      args.time, \
                      args.experiment,
                      args.no_override_settings)

    if args.open:
        dat_fname = os.path.join(rdir, "channels.dat")
        try:
            subprocess.run(['neuroscope', dat_fname])
        except AttributeError:
            subprocess.call(['neuroscope', dat_fname])

    return 0


if __name__ == "__main__":
    r = main()
    sys.exit(r)
