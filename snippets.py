import logging
import argparse
import sys
import psycopg2

# set the log output file and the log level
logging.basicConfig(filename = "snippets.log", level = logging.DEBUG)
logging.debug("Connecting to PostgreSQL")
connection = psycopg2.connect(database="snippets")
logging.debug("Databse connection established")



# function that stores a snippet with an associated name
def put(name, snippet, hide = False):
    # message to log
    logging.info("Storing snippet {!r}: {!r} hidden = {!r}".format(name, snippet, hide))
    # create cursor object - allows SQL commands in Postgre session
    with connection, connection.cursor() as cursor:
        # make sure snippet name doesn't already exist
        try:
            # create string with SQL command and two placeholders
            command = "insert into snippets values (%s, %s, %s)"
            # run the command on the database passing command and name/snippet pair as tuple
            cursor.execute(command, (name, snippet, hide))
        except psycopg2.IntegrityError as e:
            # "undo" to get db back to original state
            connection.rollback()
            # SQL command to overwrite snippet
            command = "update snippets set message=%s, hidden=%s where keyword=%s"
            # run the command on the database passing command and name/snippet pair as tuple
            cursor.execute(command, (snippet, hide, name))
        # save changes to db
        connection.commit()
    # message to log
    logging.debug("Snippet stored successfully.")
    return name, snippet, hide



# function that retreives a snippet with the name provided
def get(name):
    # message to log
    logging.info("Retrieving {!r} from databse".format(name))
    # connect wile creating cursor object - allows SQL commands in Postgre session
    with connection, connection.cursor() as cursor:
        # execute SQL command with place holder
        cursor.execute("select message from snippets where keyword=%s", (name,))
        # store in variable
        row = cursor.fetchone()
    # if no snippet was found with that name
    if not row:
        return "404: Snippet not found"
    # return the first element of the row tuple
    return row[0]

# function that retreives a list of all the keywords stored in database
def catalog():
    # messafe to log
    logging.info("Retrieving keyword list from database")
    # connect while creating cursor object - allows SQL commands in Postgre session
    with connection, connection.cursor() as cursor:
        # execute SQL command
        cursor.execute("select keyword from snippets where not hidden order by keyword")
        # store in variable
        keys = cursor.fetchall()
    # return keywords
    return keys

# function that searches for a target string in all the snippets and returns name/snippet
def search(target):
    # message to log
    logging.info("Searching for {!r} within snipperts".format(target))
    # connect while creating cursor object - allows SQL commands in Postgre session
    with connection, connection.cursor() as cursor:
        # ececute SQL command
        cursor.execute("select * from snippets where not hidden AND message like '%%'||%s||'%%'", (target,))
        # store in variable
        matches = cursor.fetchall()
    # return mathces
    return matches

# function that toggles "hide" column to true or false
def hide(name, flag):
    # message to log
    logging.info("Setting Hidden column to {!r} in {!r}".format(name, flag))
    # connect while creating cursor object - allows SQL commands in Postgre session
    with connection, connection.cursor() as cursor:
        # execute SQL command
        cursor.execute("update snippets set hidden=%s where keyword=%s", (flag, name))
    # save changes to db
    connection.commit()
    # message to log
    logging.debug("Snippet updated succesfully")
    return name, flag



def main():
    logging.info("Construction parser")
    parser = argparse.ArgumentParser(description = "Store and retreive snippets of text")
    
    subparsers = parser.add_subparsers(dest = "command", help = "Available commands")
    
    logging.debug("Constructing put subparser")
    
    # subparser for put command
    put_parser = subparsers.add_parser("put", help = "Store a snippet")
    put_parser.add_argument("name", help = "The name of the snippet")
    put_parser.add_argument("snippet", help = "The snippet of text")
    put_parser.add_argument("--hide", help = "Optional to hide snippet, default = false", action = "store_true")
    
    # subparser for get command
    get_parser = subparsers.add_parser("get", help = "Retrieve a snippet")
    get_parser.add_argument("name", help = "The name of the desired snippet")
    
    # subparser for catalog command (takes no arguments)
    catalog_parser = subparsers.add_parser("catalog", help = "Retrieve list of keywords")
    
    # subpraser for search command
    search_parser = subparsers.add_parser("search", help = "Search for string in snippets")
    search_parser.add_argument("target", help = "String of text to search within snippets")
    
    # subpraser for hide command
    hide_parser = subparsers.add_parser("hide", help = "Toggles hide column to true or false")
    hide_parser.add_argument("name", help = "Name of snippet to edit")
    hide_parser.add_argument("flag", choices = ["True", "False"], help = "Can be True or False")
    
    arguments = parser.parse_args(sys.argv[1:])
    
    # convert arguments from Namespace to dictionary
    arguments = vars(arguments)
    command = arguments.pop("command")
    
    # run command and print
    if command == "put":
        name, snippet, hidden = put(**arguments)
        if hidden == True:
            print("Stored {!r} hidden as {!r}".format(snippet, name))
        else:
            print("Stored {!r} as {!r}".format(snippet, name))
    elif command == "get":
        snippet = get(**arguments)
        print("Retreived snippet: {!r}".format(snippet))
    elif command == "catalog":
        names = catalog()
        print("Available keywords:")
        for each in names:
            print(each[0])
    elif command == "search":
        hits = search(**arguments)
        print("Matches found:")
        for each in hits:
            print(each[0] + ": " + each[1])
    elif command == "hide":
        name, flag = hide(**arguments)
        print("Hide column of {!r} set to {!r}".format(name, flag))
    


if __name__ == "__main__":
    main()