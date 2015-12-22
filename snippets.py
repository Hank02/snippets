import logging

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