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
from tempfile import TemporaryDirectory

from convert import convert_rhd


def run_neuroscope(dat_fname):
    try:
        subprocess.run(['neuroscope', dat_fname])
    except AttributeError:
        subprocess.call(['neuroscope', dat_fname])


def main():
    parser = argparse.ArgumentParser(description="Convert Intan RHD files into .dat files and Neuroscope metadata")
    parser.add_argument("fname", help="Intan RHD file")
    parser.add_argument("--open", help="Open Neuroscope", action='store_true')
    parser.add_argument("--temporary", help="Do not permanently store the converted data", action='store_true')
    parser.add_argument("--override", help="Override potentially existing files and metadata", action='store_true')
    args = parser.parse_args()

    if not args.fname:
        print("No file name given!")
        return 1


    # target directory
    nsdir = os.path.join(os.path.dirname(args.fname), "ns")
    if args.temporary:
        with TemporaryDirectory(prefix='rhd2ns-') as tmpdir:
            dat_fname = convert_rhd(args.fname, tmpdir, True)
            if args.open:
                run_neuroscope(dat_fname)
    else:
        dat_fname = convert_rhd(args.fname, nsdir, args.override)
        if args.open:
            run_neuroscope(dat_fname)

    return 0


if __name__ == "__main__":
    r = main()
    sys.exit(r)
