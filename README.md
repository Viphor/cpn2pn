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

Options:                                                                                                                                          
  -h, --help                Prints this text.                                                                                                     
  -o, --output-file <file>  Prints the PNML to the specified file instead of stdio.                                                               
  -v, --verbose             Prints additional information such as size of input and output.
```
