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
def put(name, snippet):
    # message to log
    logging.info("Storing snippet {!r}: {!r}".format(name, snippet))
    # create cursor object - allows SQL commands in Postgre session
    
    with connection, connection.cursor() as cursor:
        # make sure snippet name doesn't already exist
        try:
            # create string with SQL command and two placeholders
            command = "insert into snippets values (%s, %s)"
            # run the command on the database passing command and name/snippet pair as tuple
            cursor.execute(command, (name, snippet))
        except psycopg2.IntegrityError as e:
            # "undo" to get db back to original state
            connection.rollback()
            # SQL command to overwrite snippet
            command = "update snippets set message=%s where keyword=%s"
            # run the command on the database passing command and name/snippet pair as tuple
            cursor.execute(command, (snippet, name))
        # save changes to db
        connection.commit()
    # message to log
    logging.debug("Snippet stored successfully.")
    return name, snippet


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
        cursor.execute("select keyword from snippets order by keyword")
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
        cursor.execute("select * from snippets where message like '%%'||%s||'%%'", (target,))
        # store in variable
        matches = cursor.fetchall()
    # return mathces
    return matches
    



def main():
    logging.info("Construction parser")
    parser = argparse.ArgumentParser(description = "Store and retreive snippets of text")
    
    subparsers = parser.add_subparsers(dest = "command", help = "Available commands")
    
    logging.debug("Constructing put subparser")
    
    # subparser for put command
    put_parser = subparsers.add_parser("put", help = "Store a snippet")
    put_parser.add_argument("name", help = "The name of the snippet")
    put_parser.add_argument("snippet", help = "The snippet of text")
    
    # subparser for get command
    get_parser = subparsers.add_parser("get", help = "Retrieve a snippet")
    get_parser.add_argument("name", help = "The name of the desired snippet")
    
    # subparser for catalog command (takes no arguments)
    catalog_parser = subparsers.add_parser("catalog", help = "Retrieve list of keywords")
    
    # subpraser for search commend
    search_parser = subparsers.add_parser("search", help = "Search for string in snippets")
    search_parser.add_argument("target", help = "String of text to search within snippets")
    
    arguments = parser.parse_args(sys.argv[1:])
    
    # convert arguments from Namespace to dictionary
    arguments = vars(arguments)
    command = arguments.pop("command")
    
    # run command and print
    if command == "put":
        name, snippet = put(**arguments)
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
    

if __name__ == "__main__":
    main()