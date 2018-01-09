#!/usr/bin/python3

import sys
import time
import xml.etree.ElementTree as ET

from CPNParser.CPNModel import CPNModel
from CPNParser.PTModel import PTModel


def print_to_few_args():
    print("Too few arguments. Try -h to view help.")
    exit(0)


def print_help():
    print("Usage:")
    print("  {0} [options] <source> <target>")
    print("")
    print("  Where <source> is the file to convert, and <target> is the file for the output.")
    print("")
    print("Options:")
    print("  -v, --verbose    Prints additional information such as size of input and output")
    print("  -h, --help       Prints this text")


def verbose():
    if len(sys.argv) < 4:
        print_to_few_args()

    cpn = CPNModel(sys.argv[len(sys.argv) - 2])
    start_time = time.time()
    pt = cpn.to_pt_net()
    unfold_time = time.time() - start_time

    cpn_places = len(cpn.places.keys())
    cpn_transitions = len(cpn.transitions.keys())
    cpn_size = cpn_places + cpn_transitions

    pt_places = len(pt.places.keys())
    pt_transitions = len(pt.transitions.keys())
    pt_size = pt_places + pt_transitions

    print("Net id: ", cpn.name)
    print("Number of places in CPN: ", cpn_places)
    print("Number of transitions in CPN: ", cpn_transitions)
    print("Size in total (places+transitions): ", cpn_size)
    print("")
    print("Number of places in PT: ", pt_places)
    print("Number of transitions in PT: ", pt_transitions)
    print("Size in total (places+transitions): ", pt_size)
    print("")
    print("Size ratio: ", pt_size / cpn_size)
    print("Unfolding time: {0} seconds".format(unfold_time))

    write_net(pt, sys.argv[len(sys.argv) - 1])


def write_net(model: PTModel, output: str=None):
    if output:
        model.to_pnml().write(output, short_empty_elements=False)
    else:
        print(ET.tostring(model.to_pnml().getroot(), short_empty_elements=False))


if len(sys.argv) < 2:
    print_to_few_args()

try:
    # Add support for output files, in order to allow printing to stdout
    {
        '-v': verbose,
        '--verbose': verbose,
        '-h': print_help,
        '--help': print_help
    }[sys.argv[1]]()
except ValueError:
    if len(sys.argv) < 3:
        print_to_few_args()
    write_net(CPNModel(sys.argv[len(sys.argv) - 2]).to_pt_net(), sys.argv[len(sys.argv) - 1])
