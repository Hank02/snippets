import logging
import argparse
import sys

# set the log output file and the log level
logging.basicConfig(filename = "snippets.log", level = logging.DEBUG)

def put(name, snippet):
    # store a snippet with an associated name
    logging.error("FIXME: Unimplemented - put {!r}, {!r}".format(name, snippet))
    # return the name and snippet
    return name, snippet

def get(name):
    # retreive the snippet with the name provided
    logging.error("FIXME: Unimplemented - get({!r})".format(name))
    # return snippet
    return ""

def main():
    logging.info("Construction parser")
    parser = argparse.ArgumentParser(description = "Store and retreive snippets of text")
    
    subparsers = parser.add_subparsers(dest = "command", help = "Available commands")
    
    logging.debug("Constructing put subparser")
    put_parser = subparsers.add_parser("put", help = "Store a snippet")
    put_parser.add_argument("name", help = "The name of the snippet")
    put_parser.add_argument("snippet", help = "The snippet of text")
    
    arguments = parser.parse_args(sys.argv[1:])
    
    
if __name__ == "__main__":
    main()