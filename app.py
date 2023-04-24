'''
MIT License

Copyright (c) 2019 Arshdeep Bahga and Vijay Madisetti

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

#!flask/bin/python
from flask import Flask, jsonify, abort, request, make_response, url_for, session
from flask import render_template, redirect
from flask_session import Session
import os
import boto3
import time
import datetime
import pymongo
from flask_mysqldb import MySQL
import exifread
import json
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, static_url_path="")
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

app.config['MYSQL_HOST'] = os.getenv('DATABASE_URL')
app.config['MYSQL_USER'] = os.getenv('DATABASE_USER')
app.config['MYSQL_PASSWORD'] = os.getenv('DATABASE_PASSWORD')
app.config['MYSQL_DB'] = 'project4database'

mysql = MySQL(app)

UPLOAD_FOLDER = os.path.join(app.root_path, 'media')
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])
AWS_ACCESS_KEY=os.getenv('AWS_ACCESS_KEY')
AWS_SECRET_KEY=os.getenv('AWS_SECRET_KEY')
REGION="us-east-1"
BUCKET_NAME="project-three-photo-storage"

client = pymongo.MongoClient(os.getenv('MONGO_URI'))
db = client['photogallery']
photo_collection = db['photo_gallery_mongo_db']
user_collection = db['user_db_photo_gallery']

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.errorhandler(400)
def bad_request(error):
    return make_response(jsonify({'error': 'Bad request'}), 400)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

def getExifData(path_name):
    with open(path_name, 'rb') as f:
        tags = exifread.process_file(f)

    ExifData={}
    for tag in tags.keys():
        if tag not in ('JPEGThumbnail', 
                        'TIFFThumbnail', 
                        'Filename', 
                        'EXIF MakerNote'):            
            key=f"{tag}"
            val=f"{tags[tag]}"
            ExifData[key]=val
    return ExifData

def s3uploading(filename, filenameWithPath):
    s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY,
                            aws_secret_access_key=AWS_SECRET_KEY)
                       
    path_filename = "photos/" + filename
    print(path_filename)
    s3.upload_file(filenameWithPath, BUCKET_NAME, path_filename)  
    s3.put_object_acl(ACL='public-read', 
                Bucket=BUCKET_NAME, Key=path_filename)
    return "http://"+BUCKET_NAME+".s3.amazonaws.com/"+ path_filename  

def is_logged_in():
    return 'username' in session

@app.route('/', methods=['GET', 'POST'])
def home_page():
    logged_in = is_logged_in()

    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM metadata;')
    items = cursor.fetchall()
    cursor.close()

    categories_list = dict()
    for item in items:
        if not item[2] in categories_list:
            categories_list[item[2]] = []

        categories_list[item[2]].append(item)

    return render_template('index.html', metadata=categories_list, logged_in=logged_in)

@app.route('/<int:sectionID>/<int:categoryID>', methods=['GET'])
def category_page(sectionID, categoryID):
    logged_in = is_logged_in()

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM metadata WHERE SectionID=%s AND CategoryID=%s", (sectionID, categoryID))
    metadata = cursor.fetchone()
    section_name = metadata[2]
    category_name = metadata[3]

    cursor.execute("SELECT * FROM items WHERE SectionID=%s AND CategoryID=%s", (sectionID, categoryID))
    items = cursor.fetchall()
    cursor.close()

    return render_template('items.html', section_name=section_name, category_name=category_name, items=items, logged_in=logged_in)

def get_metadata(sectionID: int, categoryID: int):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM metadata WHERE SectionID=%s AND CategoryID=%s", (sectionID, categoryID))
    metadata = cursor.fetchone()
    cursor.close()
    return metadata

def get_item(itemID):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM items WHERE itemID=%s", (itemID,))
    item = cursor.fetchone()
    cursor.close()
    return item

@app.route('/<int:sectionID>/<int:categoryID>/<int:itemID>', methods=['GET'])
def item_page(sectionID, categoryID, itemID):
    logged_in = is_logged_in()

    metadata = get_metadata(sectionID, categoryID)
    section_name = metadata[2]
    category_name = metadata[3]
    
    item = get_item(itemID)

    item_slots = item[6:]
    metadata_slots = metadata[4:]
    slots = list(zip(metadata_slots, item_slots))

    return render_template('item.html', section_name=section_name, category_name=category_name, item=item, slots=slots, logged_in=logged_in)

@app.route('/add', methods=['GET', 'POST'])
def add_photo():
    if not is_logged_in():
        return redirect(url_for('login_page'))

    if request.method == 'POST':    
        uploadedFileURL=''

        file = request.files['imagefile']
        title = request.form['title']
        tags = request.form['tags']
        description = request.form['description']
        new_width = request.form.get('newwidth', '').strip()
        new_height = request.form.get('newheight', '').strip()

        if new_width != '':
            new_width = int(new_width)
        if new_height != '':
            new_height = int(new_height)
        
        if file and allowed_file(file.filename):
            filename = file.filename
            filenameWithPath = os.path.join(UPLOAD_FOLDER, filename)
            print(filenameWithPath)
            file.save(filenameWithPath)

            uploadedFileURL = s3uploading(filename, filenameWithPath)
            ExifData=getExifData(filenameWithPath)
            ts=time.time()
            timestamp = datetime.datetime.\
                        fromtimestamp(ts).\
                        strftime('%Y-%m-%d %H:%M:%S')

            photo_collection.insert_one(
            {
                    "PhotoID": int(ts*1000),
                    "CreationTime": timestamp,
                    "Title": title,
                    "Description": description,
                    "Tags": tags,
                    "URL": uploadedFileURL,
                    "ExifData": json.dumps(ExifData),
                    "Username": session["username"]
                }
            )

        return redirect('/')
    else:
        return render_template('form.html')

@app.route('/<int:photoID>', methods=['GET'])
def view_photo(photoID):
    logged_in = is_logged_in()

    response = photo_collection.find_one({'PhotoID': photoID})

    response['ExifData'] = response['ExifData'].replace('""', '"')
    if response['ExifData'].startswith('"'):
        response['ExifData'] = response['ExifData'][1:-1]

    tags=response['Tags'].split(',')
    exifdata=json.loads(response['ExifData'])

    return render_template('photodetail.html', 
            photo=response, tags=tags, exifdata=exifdata, logged_in=logged_in)

@app.route('/search', methods=['GET'])
def search_page():
    query = request.args.get('query', None)    
    
    response = photo_collection.find({"$or": [{"Title": {"$regex": query, "$options" : "i"}}, {'Description': {"$regex": query, "$options" : "i"}}, {'Tags': {"$regex": query, "$options" : "i"}}]})
    items = [item for item in response]

    return render_template('search.html', photos=items, searchquery=query)

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        response = user_collection.find_one({'username': username})
        item = response
        if item:
            item_pw = item["password"]
            if item_pw == password:
                # Successful login
                session['username'] = username
                return redirect('/')
            else:
                return render_template('login.html', message="Error: Incorrect Password")
        else:
            return render_template('login.html', message="Error: Username does not exist")
    
    message = request.args.get('message', None)

    return render_template('login.html', message=message)

@app.route('/signup', methods=['GET', 'POST'])
def signup_page():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if user already exists
        item = user_collection.find_one({"username": username})

        user_already_exists = True if item else False
        if user_already_exists:
            return render_template('signup.html', message='Error: User already exists')
        
        user_collection.insert_one({
                    "username": username,
                    "password": password
                })

        # Redirect to login page
        return redirect(url_for('login_page', message='Successfully signed up! Login to get started.'))

    return render_template('signup.html')

@app.route("/logout")
def logout():
    del session['username']
    return redirect("/")

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5001)
