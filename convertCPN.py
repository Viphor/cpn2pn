#!/usr/bin/python3

import sys

from CPNParser.CPNModel import CPNModel

if len(sys.argv) < 3:
    print("Too few arguments.")
    print("  Usage:")
    print("     {0} <source> <target>")
    print("  Where <source> is the file to convert, and <target> is the file for the output.")
    exit(0)

CPNModel(sys.argv[1]).to_pt_net().to_pnml().write(sys.argv[2], short_empty_elements=False)
