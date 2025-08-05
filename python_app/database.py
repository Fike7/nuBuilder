# -*- coding: utf-8 -*-

import mysql.connector
from mysql.connector import errorcode
from . import config

def get_db_connection():
    """
    Establishes and returns a database connection using settings from config.py.
    """
    try:
        cnx = mysql.connector.connect(
            user=config.DB_USER,
            password=config.DB_PASSWORD,
            host=config.DB_HOST,
            database=config.DB_NAME,
            port=config.DB_PORT,
            **config.DB_OPTIONS
        )
        return cnx
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Database Error: Access denied. Check username or password.")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print(f"Database Error: Database '{config.DB_NAME}' does not exist.")
        else:
            print(f"Database Error: {err}")
        return None

def run_query(sql, params=None, fetch=None, is_insert=False):
    """
    Executes a SQL query and returns the result.

    Args:
        sql (str): The SQL query string with '%s' placeholders.
        params (tuple, optional): A tuple of parameters to bind to the query.
        fetch (str, optional): "one" to fetch a single row, "all" to fetch all rows.
                               If None, the query is executed without fetching results (e.g., for UPDATE).
        is_insert (bool, optional): If True, commits the transaction and returns the last inserted row ID.

    Returns:
        The result of the query (dict, list of dicts, int) or None if an error occurs.
    """
    cnx = get_db_connection()
    if not cnx:
        return None

    # dictionary=True returns rows as dictionaries, similar to PHP's associative arrays
    cursor = cnx.cursor(dictionary=True)

    try:
        cursor.execute(sql, params or ())

        if is_insert:
            last_id = cursor.lastrowid
            cnx.commit()
            return last_id

        if fetch == "one":
            return cursor.fetchone()
        elif fetch == "all":
            return cursor.fetchall()
        else:
            # For statements that modify data but aren't inserts (UPDATE, DELETE)
            if cursor.rowcount > 0:
                cnx.commit()
            return cursor.rowcount

    except mysql.connector.Error as err:
        # Basic error logging, similar to nuDebug
        print(f"SQL Error: {err}")
        print(f"Query: {sql}")
        if params:
            print(f"Params: {params}")
        cnx.rollback() # Rollback on error
        return None
    finally:
        cursor.close()
        cnx.close()
