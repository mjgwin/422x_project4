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

# Sections
FOR_SALE = '0'
HOUSING = '1'
SERVICES = '2'
JOBS = '3'
COMMUNITY = '4'

# For Sale
FOR_SALE_NAME = 'For Sale'
CELL_PHONE = '0'; CELL_PHONE_NAME = 'Cell Phones'
APPLIANCES = '1'; APPLIANCES_NAME = 'Appliances'
AUTOPARTS = '2'; AUTOPARTS_NAME = 'Auto Parts'
BOOKS = '3'; BOOKS_NAME = 'Books'
FURNITURE = '4'; FURNITURE_NAME = 'Furniture'

# Housing
HOUSING_NAME = 'Housing'
HOUSE_SWAP = '0'; HOUSE_SWAP_NAME = 'House Swap'
ROOMS_WANTED = '1'; ROOMS_WANTED_NAME = 'Rooms Wanted'
COMMERCIAL = '2'; COMMERCIAL_NAME = 'Commercial'
STORAGE = '3'; STORAGE_NAME = 'Storage'
SUBLETS = '4'; SUBLETS_NAME = 'Sublets'

# Services
SERVICES_NAME = 'Services'
AUTOMOTIVE = '0'; AUTOMOTIVE_NAME = 'Automotive'
LESSONS_TUTORING = '1'; LESSONS_TUTORING_NAME = 'Lessons/Tutoring'
TRANSPORTATION = '2'; TRANSPORTATION_NAME = 'Transportation'
LANDSCAPING = '3'; LANDSCAPING_NAME = 'Landscaping'
LEGAL = '4'; LEGAL_NAME = 'Legal'

# Jobs
JOBS_NAME = 'Jobs'
FINANCE = '0'; FINANCE_NAME = 'Finance'
REAL_ESTATE = '1'; REAL_ESTATE_NAME = 'Real Estate'
EDUCATION = '2'; EDUCATION_NAME = 'Education'
SOFTWARE = '3'; SOFTWARE_NAME = 'Software'
MISCELLANEOUS = '4'; MISCELLANEOUS_NAME = 'Miscellaneous'

# Community
COMMUNITY_NAME = 'Community'
EVENTS = '0'; EVENTS_NAME = 'Events'
CONNECTIONS = '1'; CONNECTIONS_NAME = 'Connections'
PETS = '2'; PETS_NAME = 'Pets'
LOCALNEWS = '3'; LOCALNEWS_NAME = 'Local News'
VOLUNTEERS = '4'; VOLUNTEERS_NAME = 'Volunteers'

insert_metadata = f"""INSERT INTO metadata
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
"""

insert_item = f"""INSERT INTO items(
    SectionID,
    CategoryID,
    ImageUrl,
    PostedBy,
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
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
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
        (FOR_SALE, APPLIANCES, FOR_SALE_NAME, APPLIANCES_NAME, 'Type', 'Manufacturer', 'Power Consumption', 'Model Version', 'Price', 'Condition', 'Warranty Included', 'Appearance'),
        # Auto Parts
        (FOR_SALE, BOOKS, FOR_SALE_NAME, BOOKS_NAME, 'Name', 'Author', 'Page Count', 'ISBN', 'Condition', 'Format', 'Publisher', 'Price'),
        # Furniture
    ],
    HOUSING: [
        (HOUSING, HOUSE_SWAP, HOUSING_NAME, HOUSE_SWAP_NAME, 'Address', 'Square Ft', 'Pet Friendly', 'Storage', 'Smoking Friendly', 'AC', 'Apartment', 'Washer/Dryer'),
        # Rooms Wanted
        # Commercial
        # Storage
        # Sublets
    ],
    SERVICES: [
        # Automotive
        # Lessons/Tutoring
        # Transportation
        # Landscaping
        # Legal
    ],
    JOBS: [
        # Finance
        # Real Estate
        # Education
        (JOBS, SOFTWARE, JOBS_NAME, SOFTWARE_NAME, 'Company Name', 'Employment Type', 'Job Title', 'Compensation', 'Benefits', 'Skills/Languages', 'PTO', 'Clearances/Requirements'),
        # Miscellaneous
    ],
    COMMUNITY: [
        (COMMUNITY, EVENTS, COMMUNITY_NAME, EVENTS_NAME, 'Address', 'Date', 'Type', 'Time', 'Adult Price', 'Child Price', 'Food/Drink', 'Venue'),
        # Connections
        (COMMUNITY, PETS, COMMUNITY_NAME, PETS_NAME, 'Animal', 'Age', 'Spayed/Neutered', 'Vaccinated', 'Color', 'Count', 'Good With Kids', 'Price'),
        # Local news
        # Volunteers
    ]
}

clear_metadata()
for metadata_array in metadata_items.values():
    for metadata_item in metadata_array:
        insert_into_metadata(metadata_item)


items = [
    (FOR_SALE, CELL_PHONE, 'https://project-four-photo-storage.s3.amazonaws.com/iphone14problack.jpg', 'se422x', 'iPhone 14 Space Gray 256GB', 'do NOT contact me with unsolicited services or offers', 'Apple', 'iPhone 14', 'Space Gray', '256GB', '8GB', 'Verizon', 'Used', '$300')
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
