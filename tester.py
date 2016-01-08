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
            # save changes to db
            connection.commit()
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
    
    arguments = parser.parse_args(sys.argv[1:])
    
    # convert arguments from Namespace to dictionary
    arguments = vars(arguments)
    command = arguments.pop("command")
    if command == "put":
        name, snippet = put(**arguments)
        print("Stored {!r} as {!r}".format(snippet, name))
    elif command == "get":
        snippet = get(**arguments)
        print("Retreived snippet: {!r}".format(snippet))
    

if __name__ == "__main__":
    main()