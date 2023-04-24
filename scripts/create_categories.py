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

insert_item = f"""INSERT INTO items(
    SectionID,
    CategoryID,
    ImageKey,
    Title,
    Description,
    Slot0,
    Slot1,
    Slot2,
    Slot3,
    Slot4,
    Slot5,
    Slot6,
    Slot7
)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
"""

def clear_metadata():
    r = cursor.execute('DELETE FROM metadata;')
    cursor.connection.commit()
    return r
    
def clear_items():
    r = cursor.execute('DELETE FROM items;')
    cursor.connection.commit()
    return r

def insert_into_metadata(values: tuple[Union[str, int], ...]):
    try:
        cursor.execute(insert_metadata, values)
    except Exception as e:
        print(f"Failed to insert into metadata, error: {str(e)}")
        return
    cursor.connection.commit()

def insert_into_items(values: tuple[Union[str, int], ...]):
    try:
        cursor.execute(insert_item, values)
    except Exception as e:
        print(f"Failed to insert into metadata, error: {str(e)}")
        return
    cursor.connection.commit()

metadata_items = {
    FOR_SALE: [
        (FOR_SALE, CELL_PHONE, FOR_SALE_NAME, CELL_PHONE_NAME, 'Manufacturer', 'Model', 'Color', 'Storage', 'RAM', 'Carrier', 'Condition', 'Price'),
        (FOR_SALE, APPLIANCES, FOR_SALE_NAME, APPLIANCES_NAME, 'Type', 'Manufacturer', 'Power Consumption', 'Model Version', 'Price', 'Condition', 'Warranty Included', 'Appearance')
    ],
    HOUSING: [
        (HOUSING, HOUSE_SWAP, HOUSING_NAME, HOUSE_SWAP_NAME, 'Address', 'Square Ft', 'Pet Friendly', 'Storage', 'Smoking Friendly', 'AC', 'Apartment', 'Washer/Dryer')
    ]
}

clear_metadata()
for metadata_array in metadata_items.values():
    for metadata_item in metadata_array:
        insert_into_metadata(metadata_item)


items = [
    (FOR_SALE, CELL_PHONE, '', 'iPhone 14 Red 256GB', 'do NOT contact me with unsolicited services or offers', 'Apple', 'iPhone 14', 'Red', '256GB', '8GB', 'Verizon', 'Used', '$300')
]

clear_items()
for items in items:
    insert_into_items(items)

cursor.execute('SELECT * from metadata;')
res = cursor.fetchall()
print('Metadata: ' + str(res))

cursor.execute('SELECT * from items;')
res = cursor.fetchall()
print('Items: ' + str(res))
