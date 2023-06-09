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
HOUSE_SWAP = '5'; HOUSE_SWAP_NAME = 'House Swap'
ROOMS_WANTED = '6'; ROOMS_WANTED_NAME = 'Rooms Wanted'
COMMERCIAL = '7'; COMMERCIAL_NAME = 'Commercial'
STORAGE = '8'; STORAGE_NAME = 'Storage'
SUBLETS = '9'; SUBLETS_NAME = 'Sublets'

# Services
SERVICES_NAME = 'Services'
AUTOMOTIVE = '10'; AUTOMOTIVE_NAME = 'Automotive'
LESSONS_TUTORING = '11'; LESSONS_TUTORING_NAME = 'Lessons/Tutoring'
TRANSPORTATION = '12'; TRANSPORTATION_NAME = 'Transportation'
LANDSCAPING = '13'; LANDSCAPING_NAME = 'Landscaping'
LEGAL = '14'; LEGAL_NAME = 'Legal'

# Jobs
JOBS_NAME = 'Jobs'
FINANCE = '15'; FINANCE_NAME = 'Finance'
REAL_ESTATE = '16'; REAL_ESTATE_NAME = 'Real Estate'
EDUCATION = '17'; EDUCATION_NAME = 'Education'
SOFTWARE = '18'; SOFTWARE_NAME = 'Software'
RETAIL = '19'; RETAIL_NAME = 'Retail'

# Community
COMMUNITY_NAME = 'Community'
EVENTS = '20'; EVENTS_NAME = 'Events'
LOST_FOUND = '21'; LOST_FOUND_NAME = 'Lost + Found'
PETS = '22'; PETS_NAME = 'Pets'
MUSICIANS = '23'; MUSICIANS_NAME = 'Musicians'
VOLUNTEERS = '24'; VOLUNTEERS_NAME = 'Volunteers'

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
        (FOR_SALE, AUTOPARTS, FOR_SALE_NAME, AUTOPARTS_NAME, 'Manufacturer', 'Model', 'Condition', 'Type', 'Fits', 'Dimensions', 'Color', 'Price'),
        (FOR_SALE, BOOKS, FOR_SALE_NAME, BOOKS_NAME, 'Name', 'Author', 'Page Count', 'ISBN', 'Condition', 'Format', 'Publisher', 'Price'),
        (FOR_SALE, FURNITURE, FOR_SALE_NAME, FURNITURE_NAME, 'Type', 'Manufacturer', 'Condition', 'Dimensions', 'Color', 'Weight', 'Material', 'Price'),
    ],
    HOUSING: [
        (HOUSING, HOUSE_SWAP, HOUSING_NAME, HOUSE_SWAP_NAME, 'Address', 'Square Feet', 'Pet Friendly', 'Storage', 'Smoking Friendly', 'AC', 'Apartment', 'Washer/Dryer'),
        (HOUSING, ROOMS_WANTED, HOUSING_NAME, ROOMS_WANTED_NAME, 'Address', 'Price', 'Square Feet', 'Max Occupancy', 'Pet Friendly', 'Kitchen Access', 'Smoking Friendly', 'Garage'),
        (HOUSING, COMMERCIAL, HOUSING_NAME, COMMERCIAL_NAME, 'Lease Rate', 'Lease Terms', 'Address', 'Square Feet', 'Contact Info', 'AC', 'Mail Service', 'Amenities'),
        (HOUSING, STORAGE, HOUSING_NAME, STORAGE_NAME, 'Price', 'Address', 'Smoke Free', 'Square Feet', 'Climate Controlled', 'Vehicle Storage', 'Security', 'Moving Assistance Provided'),
        (HOUSING, SUBLETS, HOUSING_NAME, SUBLETS_NAME, 'Address', 'Price', 'Square Feet', 'Washer/Dryer', 'Furnished', 'Pet Friendly', 'Smoking Friendly', 'Garage'),
    ],
    SERVICES: [
        (SERVICES, AUTOMOTIVE, SERVICES_NAME, AUTOMOTIVE_NAME, 'Service Type', 'Certified', 'Insured', 'Address', 'Price', 'Contact Info', 'Payment Types', 'Willing to Travel'),
        (SERVICES, LESSONS_TUTORING, SERVICES_NAME, LESSONS_TUTORING_NAME, 'Service Type', 'Experience Level', 'Address', 'Price', 'Contact Info', 'Delivery Method', 'Willing to Travel', 'Certified'),
        (SERVICES, TRANSPORTATION, SERVICES_NAME, TRANSPORTATION_NAME, 'Type', 'Price', 'Distance Range', 'Contact Info', 'Storage Capacity', 'Passenger Capacity', 'Payments Accepted', 'Years Experience'),
        (SERVICES, LANDSCAPING, SERVICES_NAME, LANDSCAPING_NAME, 'Type', 'Contact Info', 'Tools Required', 'Distance Range', 'Price', 'Payments Accepted', 'Free Estimates', 'Years Experience'),
        (SERVICES, LEGAL, SERVICES_NAME, LEGAL_NAME, 'Type', 'Contact Info', 'Address', 'Price', 'Years Experience', 'Certifications', 'Free Consultation', 'Website'),
    ],
    JOBS: [
        (JOBS, FINANCE, JOBS_NAME, FINANCE_NAME, 'Employer Name', 'Employment Type', 'Job Title', 'Compensation', 'Address', 'Benefits', 'Responsibilities', 'Years Experience'),
        (JOBS, REAL_ESTATE, JOBS_NAME, REAL_ESTATE_NAME, 'Employer Name', 'Employment Type', 'Job Title', 'Compensation', 'Address', 'Requirements', 'Benefits', 'Job Duties'),
        (JOBS, EDUCATION, JOBS_NAME, EDUCATION_NAME, 'Employer Name', 'Employment Type', 'Job Title', 'Compensation', 'Grade/Age Range', 'Address', 'Qualifications', 'Website'),
        (JOBS, SOFTWARE, JOBS_NAME, SOFTWARE_NAME, 'Employer Name', 'Employment Type', 'Job Title', 'Compensation', 'Benefits', 'Skills/Languages', 'PTO', 'Clearances/Requirements'),
        (JOBS, RETAIL, JOBS_NAME, RETAIL_NAME, 'Employer Name', 'Employment Type', 'Job Title', 'Compensation', 'Address', 'Qualifications', 'Duties/Responsibilities', 'Application Link'),
    ],
    COMMUNITY: [
        (COMMUNITY, EVENTS, COMMUNITY_NAME, EVENTS_NAME, 'Address', 'Date', 'Type', 'Time', 'Adult Price', 'Child Price', 'Food/Drink', 'Venue'),
        (COMMUNITY, LOST_FOUND, COMMUNITY_NAME, LOST_FOUND_NAME, 'Item Name', 'Item Color', 'Item Size', 'Last Location', 'In Possession', 'Date and Time Lost/Found', 'Phone Number', 'Reward'),
        (COMMUNITY, PETS, COMMUNITY_NAME, PETS_NAME, 'Animal', 'Age', 'Spayed/Neutered', 'Vaccinated', 'Color', 'Count', 'Good With Kids', 'Price'),
        (COMMUNITY, MUSICIANS, COMMUNITY_NAME, MUSICIANS_NAME, 'Location', 'Instrument(s)', 'Genre', 'Website', 'Gig', 'Venue', 'Day', 'Age Range'),
        (COMMUNITY, VOLUNTEERS, COMMUNITY_NAME, VOLUNTEERS_NAME, 'Task', 'Date', 'Time', 'Location', 'Age Requirement', 'Website', 'Duties', 'Recurring'),
    ]
}

clear_metadata()
for metadata_array in metadata_items.values():
    for metadata_item in metadata_array:
        insert_into_metadata(metadata_item)


# Insert items on frontend
# items = [
#     (FOR_SALE, CELL_PHONE, 'https://project-four-photo-storage.s3.amazonaws.com/iphone14problack.jpg', 'se422x', 'iPhone 14 Space Gray 256GB', 'do NOT contact me with unsolicited services or offers', 'Apple', 'iPhone 14', 'Space Gray', '256GB', '8GB', 'Verizon', 'Used', '$700'),
#     (FOR_SALE, CELL_PHONE, 'https://project-four-photo-storage.s3.amazonaws.com/samsung-galaxy-s22-ultra-3-1644951721.jpg', 'se422x', 'Samsung S22 Ultra like new', 'do NOT contact me with unsolicited services or offers', 'Samsung', 'S22 Ultra', 'Black', '128GB', '12GB', 'Unlocked', 'Like New', '$500'),
#     (FOR_SALE, CELL_PHONE, 'https://project-four-photo-storage.s3.amazonaws.com/iphone14problack.jpg', 'se422x', 'iPhone 14 Space Gray 256GB', 'do NOT contact me with unsolicited services or offers', 'Apple', 'iPhone 14', 'Space Gray', '256GB', '8GB', 'Verizon', 'Used', '$300'),
# ]
#
# clear_items()
# for items in items:
#     insert_into_items(items)

cursor.execute('SELECT * from metadata;')
res = cursor.fetchall()
print('Metadata: ' + str(res))

cursor.execute('SELECT * from items;')
res = cursor.fetchall()
print('Items: ' + str(res))
