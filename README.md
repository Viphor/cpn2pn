# cpn2pn
Transform Coloured Petri Nets in PNML format to equivalent Petri Nets

This project is written for python 3.6+ and uses the dependency multiset,
which can be installed by:

```
$ pip install multiset
```

## Usage:
This project is written as a module called CPNParser, which contains the models
used for reading Coloured Petri Nets in PNML format, the code for unfolding the net,
and the model for Petri Nets, which can be converted to PNML format.

The input file must follow the PNML standard for symmetric nets in order to be parsed.
More information on the standard can be found at [pnml.org](http://www.pnml.org/) and 
in this [paper](http://www.pnml.org/papers/pnnl76.pdf).

### Command line
In order to access this functionality from the command line, the tool convertCPN.py
was written. To get help, use:

```
$ convertCPN.py -h
ConvertCPN is a tool that converts a colored Petri net in the PNML format, to a P/T net,
and prints the P/T net to stdout in PNML format.

Usage:
  convertCPN.py [options] <source>

  Where <source> is the file to convert.
  Note: stderr is used for outputting inconsistencies with the PNML standand.

Options:                                                                                                                                          
  -h, --help                Prints this text.                                                                                                     
  -o, --output-file <file>  Prints the PNML to the specified file instead of stdout.                                                               
  -v, --verbose             Prints additional information such as size of input and output.
```

## TODO
- Rewrite tests to not require not included files
- Make the single- and multi-threaded sections as functions (found at comments "# TODO:1")
