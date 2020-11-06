import psycopg2
from dotenv import load_dotenv
load_dotenv()
import os

conn = psycopg2.connect(
database=os.getenv("PG_DATABASE"),
user=os.getenv("PG_USER"),
password=os.getenv("PG_PASSWORD"),
host=os.getenv("PG_HOST"),
port=os.getenv("PG_PORT"))

db = conn.cursor()

db.execute( # Creates the 'users' table
"""
CREATE TABLE users (
    id INTEGER PRIMARY KEY NOT NULL,
    username VARCHAR(30) NOT NULL,
    email VARCHAR(100) NOT NULL,
    hash VARCHAR(256) NOT NULL,

    UNIQUE (email),
    UNIQUE (username)
)
"""
)
print("'users' table sucessfully created!")

conn.commit()
conn.close()

