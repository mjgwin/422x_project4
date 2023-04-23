import os
from typing import Union
import pymysql
from dotenv import load_dotenv

load_dotenv()

database_password = os.getenv('DATABASE_PASSWORD')
if database_password is None:
    raise ValueError('set env var DATABASE_PASSWORD')

db = pymysql.connect(host=os.getenv('DATABASE_URL'), user = os.getenv('DATABASE_USER'), password = database_password)

cursor = db.cursor()
cursor.execute('USE project4database;')
cursor.connection.commit()

FOR_SALE = '0'
FOR_SALE_NAME = 'For Sale'
HOUSING = '1'
HOUSING_NAME = 'Housing'
HOUSE_SWAP = '0'
HOUSE_SWAP_NAME = 'House Swap'
CELL_PHONE = '0'
CELL_PHONE_NAME = 'Cell Phones'
APPLIANCES = '1'
APPLIANCES_NAME = 'Appliances'

insert_metadata = f"""INSERT INTO metadata
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
"""

def clear_metadata():
    r = cursor.execute('DELETE FROM metadata;')
    cursor.connection.commit()
    return r

# clear_metadata()

def insert_into_metadata(values: tuple[Union[str, int], ...]):
    try:
        cursor.execute(insert_metadata, values)
    except Exception as e:
        print(f"Failed to insert into metadata, error: {str(e)}")
        return
    cursor.connection.commit()

# Cell Phones
insert_into_metadata((FOR_SALE, CELL_PHONE, FOR_SALE_NAME, CELL_PHONE_NAME, 'Manufacturer', 'Model', 'Color', 'Storage', 'RAM', 'Carrier', 'Condition', 'Price'))

# Appliances
insert_into_metadata((FOR_SALE, APPLIANCES, FOR_SALE_NAME, APPLIANCES_NAME, 'Type', 'Manufacturer', 'Power Consumption', 'Model Version', 'Price', 'Condition', 'Warranty Included', 'Appearance'))

# House_Swap
insert_into_metadata((HOUSING, HOUSE_SWAP, HOUSING_NAME, HOUSE_SWAP_NAME, 'Address', 'Square Ft', 'Pet Friendly', 'Storage', 'Smoking Friendly', 'AC', 'Apartment', 'Washer/Dryer'))

cursor.execute('SELECT * from metadata;')
res = cursor.fetchall()
print('Metadata: ' + str(res))
