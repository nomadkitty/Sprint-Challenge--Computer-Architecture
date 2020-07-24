#!/usr/bin/env python3

"""Main."""

import sys
from cpu import *

cpu = CPU()

if len(sys.argv) < 2:
    print("Please pass in a second filename: py -3 in_and_out.py second_filename.py")
    sys.exit()

file_name = sys.argv[1]

cpu.load(file_name)
cpu.run()
