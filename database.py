import sqlite3
import pandas as pd

def get_connection(db_path='math.db'):
    """Create a connection to the SQLite database"""
    conn = sqlite3.connect(db_path)
    return conn

def execute_query(query, params=None, db_path='math.db'):
    """Execute a query and return the results as a pandas DataFrame"""
    try:
        conn = get_connection(db_path)
        if params:
            result = pd.read_sql_query(query, conn, params=params)
        else:
            result = pd.read_sql_query(query, conn)
        conn.close()
        return result
    except Exception as e:
        error_msg = f"Database error: {str(e)}\nPath: {db_path}\nQuery: {query}"
        if params:
            error_msg += f"\nParams: {params}"
        raise Exception(error_msg)

def get_table_schema(table_name, db_path='math.db'):
    """Get schema information for a specific table"""
    query = f"PRAGMA table_info({table_name})"
    return execute_query(query, db_path=db_path)

def get_all_tables(db_path='math.db'):
    """Get a list of all tables in the database"""
    query = "SELECT name FROM sqlite_master WHERE type='table';"
    result = execute_query(query, db_path=db_path)
    return result['name'].tolist()

def get_distinct_values(table, column, db_path='math.db'):
    """Get all distinct values for a specific column in a table"""
    query = f"SELECT DISTINCT {column} FROM {table} WHERE {column} IS NOT NULL ORDER BY {column}"
    result = execute_query(query, db_path=db_path)
    return result[column].tolist()