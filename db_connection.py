import mysql.connector
from mysql.connector import Error
import configparser
import os

def load_config(filename="config.ini"):
    print("Current directory:", os.getcwd())  # Debugging
    print("Files in directory:", os.listdir())  # Debugging

    if not os.path.exists(filename):
        raise FileNotFoundError(f"Config file '{filename}' not found!")

    config = configparser.ConfigParser()
    config.read(filename, encoding="utf-8")

    print("Available sections:", config.sections())  # Debugging

    if 'database' not in config:
        raise KeyError("Missing [database] section in config file")

    return config['database']

config = load_config()
print("Config loaded successfully:", dict(config))  # Debugging

def create_db_connection():
    config = configparser.ConfigParser()
    config.read('config.ini')

    try:
        connection = mysql.connector.connect(
            host=config['database']['host'],
            user=config['database']['user'],
            password=config['database']['password'],
            database=config['database']['database']
        )
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None


def close_db_connection(connection):
    if connection:
        connection.close()