#!flask/bin/python
"""
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
"""

from typing import Union
from flask import Flask, jsonify, abort, request, make_response, url_for, session
from flask import render_template, redirect
from flask_session import Session
import os
import boto3
import pymongo
from flask_mysqldb import MySQL
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
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
AWS_ACCESS_KEY=os.getenv('AWS_ACCESS_KEY')
AWS_SECRET_KEY=os.getenv('AWS_SECRET_KEY')
REGION="us-east-1"
BUCKET_NAME="project-three-photo-storage"

client = pymongo.MongoClient(os.getenv('MONGO_URI'))
db = client['photogallery']
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


@app.context_processor
def inject_enumerate():
    return dict(enumerate=enumerate)


def insert_into_items(values: tuple[Union[str, int], ...]) -> int:
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
    cursor = mysql.connection.cursor()
    try:
        cursor.execute(insert_item, values)
    except Exception as e:
        print(f"Failed to insert into item, error: {str(e)}")
        return -1
    cursor.connection.commit()
    return cursor.lastrowid


def s3uploading(filename, filenameWithPath):
    s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY,
                            aws_secret_access_key=AWS_SECRET_KEY)

    path_filename = "photos/" + filename
    s3.upload_file(filenameWithPath, BUCKET_NAME, path_filename)
    s3.put_object_acl(ACL='public-read',
                Bucket=BUCKET_NAME, Key=path_filename)
    return "http://"+BUCKET_NAME+".s3.amazonaws.com/"+ path_filename


def is_logged_in():
    return 'username' in session


def get_username():
    return session['username']


def get_query_section_category():
    sid = request.args.get('sid')
    cid = request.args.get('cid')

    if sid is None or cid is None:
        return -1, -1, redirect('/')

    sid = int(sid)
    cid = int(cid)

    return sid, cid, None


def get_metadata(section_id: int, category_id: int):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM metadata WHERE SectionID=%s AND CategoryID=%s", (section_id, category_id))
    metadata = cursor.fetchone()
    cursor.close()
    return metadata


def get_category_items(section_id: int, category_id: int):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM items WHERE SectionID=%s AND CategoryID=%s", (section_id, category_id))
    items = cursor.fetchall()
    cursor.close()
    return items


def get_item(item_id: int):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM items WHERE itemID=%s", (item_id,))
    item = cursor.fetchone()
    cursor.close()
    return item


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


@app.route('/<int:section_id>/<int:category_id>', methods=['GET'])
def category_page(section_id: int, category_id: int):
    logged_in = is_logged_in()

    metadata = get_metadata(section_id, category_id)
    section_name = metadata[2]
    category_name = metadata[3]

    items = get_category_items(section_id, category_id)

    return render_template('category.html', metadata=metadata, section_name=section_name, category_name=category_name,
                           items=items, logged_in=logged_in)


@app.route('/<int:section_id>/<int:category_id>/<int:item_id>', methods=['GET'])
def item_page(section_id: int, category_id: int, item_id: int):
    logged_in = is_logged_in()

    item = get_item(item_id)

    metadata = get_metadata(section_id, category_id)
    section_name = metadata[2]
    category_name = metadata[3]

    item_slots = item[7:]
    metadata_slots = metadata[4:]
    slots = list(zip(metadata_slots, item_slots))

    return render_template('item.html', section_name=section_name, category_name=category_name, item=item, 
                            section_id=section_id, category_id=category_id, slots=slots, logged_in=logged_in)


@app.route('/create', methods=['GET', 'POST'])
def create_item():
    if not is_logged_in():
        return redirect(url_for('login_page'))

    sid, cid, err = get_query_section_category()
    if err is not None:
        return err

    if request.method == 'POST':
        file = request.files['imagefile']
        title = request.form['title']
        description = request.form['description']
        slots = [request.form[f'slot{i}'] for i in range(0, 8)]

        # Upload file if exists
        if file and allowed_file(file.filename):
            filename = file.filename
            filename_with_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filename_with_path)

            uploaded_file_url = s3uploading(filename, filename_with_path)
        else:
            uploaded_file_url = ''

        new_item_id = insert_into_items((sid, cid, uploaded_file_url, get_username(), title, description, *slots))

        if new_item_id == -1:
            # Error
            return redirect(f'/{sid}/{cid}')

        # Redirect to item
        return redirect(f'/{sid}/{cid}/{new_item_id}')
    else:
        metadata = get_metadata(sid, cid)
        return render_template('create.html', metadata=metadata, logged_in=True)


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
    app.run(debug=True, host="0.0.0.0", port=4999)
