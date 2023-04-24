import os
import pymysql
from dotenv import load_dotenv

load_dotenv()

database_password = os.getenv('DATABASE_PASSWORD')
if database_password is None:
    raise ValueError('set env var DATABASE_PASSWORD')

db = pymysql.connect(host=os.getenv('DATABASE_URL'), user = os.getenv('DATABASE_USER'), password = database_password)

cursor = db.cursor()
cursor.execute('CREATE DATABASE IF NOT EXISTS project4database;')
cursor.execute('USE project4database;')
cursor.execute('DROP TABLE IF EXISTS items;')
cursor.execute('DROP TABLE IF EXISTS metadata;')
cursor.connection.commit()

create_items_table_query = """CREATE TABLE IF NOT EXISTS items(
    ItemID INT NOT NULL AUTO_INCREMENT,
    SectionID INT NOT NULL,
    CategoryID INT NOT NULL,
    ImageUrl TEXT NOT NULL,
    PostedBy TEXT NOT NULL,
    Title TEXT NOT NULL,
    Description TEXT NOT NULL,
    Slot0 TEXT NOT NULL,
    Slot1 TEXT NOT NULL,
    Slot2 TEXT NOT NULL,
    Slot3 TEXT NOT NULL,
    Slot4 TEXT NOT NULL,
    Slot5 TEXT NOT NULL,
    Slot6 TEXT NOT NULL,
    Slot7 TEXT NOT NULL,
    PRIMARY KEY (ItemID)
);
"""

create_metadata_table_query = """CREATE TABLE IF NOT EXISTS metadata(
    SectionID INT NOT NULL,
    CategoryID INT NOT NULL,
    SectionName TEXT NOT NULL,
    CategoryName TEXT NOT NULL,
    Slot0 TEXT NOT NULL,
    Slot1 TEXT NOT NULL,
    Slot2 TEXT NOT NULL,
    Slot3 TEXT NOT NULL,
    Slot4 TEXT NOT NULL,
    Slot5 TEXT NOT NULL,
    Slot6 TEXT NOT NULL,
    Slot7 TEXT NOT NULL,
    PRIMARY KEY (SectionID, CategoryID)
);
"""

cursor.execute(create_items_table_query)
cursor.execute(create_metadata_table_query)
cursor.connection.commit()

cursor.execute('SHOW TABLES;')
res = cursor.fetchall()
print('Tables: ' + str(res))
