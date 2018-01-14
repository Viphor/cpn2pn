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
    print("ConvertCPN is a tool that converts a colored Petri net in the PNML format, to a P/T net,")
    print("and prints the P/T net to stdout in PNML format.")
    print("")
    print("Usage:")
    print("  {0} [options] <source>")
    print("")
    print("  Where <source> is the file to convert.")
    print("")
    print("Options:")
    print("  -h, --help                Prints this text.")
    print("  -o, --output-file <file>  Prints the PNML to the specified file instead of stdio.")
    print("  -v, --verbose             Prints additional information such as size of input and output.")


def verbose():
    if len(sys.argv) < 4:
        print_to_few_args()

    cpn = CPNModel(sys.argv[len(sys.argv) - 1])

    cpn_places = len(cpn.places.keys())
    cpn_transitions = len(cpn.transitions.keys())
    cpn_size = cpn_places + cpn_transitions

    print("Net id: ", cpn.name)
    print("Number of places in CPN: ", cpn_places)
    print("Number of transitions in CPN: ", cpn_transitions)
    print("Size in total (places+transitions): ", cpn_size)
    print("")

    start_time = time.time()
    pt = cpn.to_pt_net()
    unfold_time = time.time() - start_time

    pt_places = len(pt.places.keys())
    pt_transitions = len(pt.transitions.keys())
    pt_size = pt_places + pt_transitions

    print("Number of places in PT: ", pt_places)
    print("Number of transitions in PT: ", pt_transitions)
    print("Size in total (places+transitions): ", pt_size)
    print("")
    print("Size ratio: ", pt_size / cpn_size)
    print("Unfolding time: {0} seconds".format(unfold_time))

    global output_file
    write_net(pt, output_file)


def write_net(model: PTModel, output: str=None):
    if output:
        model.to_pnml().write(output, short_empty_elements=False)
    else:
        print(ET.tostring(model.to_pnml().getroot(), short_empty_elements=False).decode('utf-8'))


def read_output_file(file=None):
    global read_output
    global output_file
    if not file:
        read_output = True
        return

    output_file = file
    read_output = False


if len(sys.argv) < 2:
    print_to_few_args()

output_file = None
read_output = False

commands = {
    '-v': verbose,
    '--verbose': verbose,
    '-h': print_help,
    '--help': print_help,
    '-o': read_output_file,
    '--output': read_output_file,
}

try:
    for arg in sys.argv[1:]:
        print(arg)
        if read_output:
            if arg in commands:
                raise Exception("A file name must follow the argument -o or --output. Try -h for more help.")
            read_output_file(arg)
            continue
        commands[arg]()
except KeyError:
    write_net(CPNModel(sys.argv[len(sys.argv) - 1]).to_pt_net(), output_file)
