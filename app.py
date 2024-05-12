from flask import Flask, render_template, request, redirect, url_for, session,send_file
from flask_login import login_required
from werkzeug.utils import secure_filename
import os
import firebase_admin
from firebase_admin import credentials, initialize_app, firestore

app = Flask(__name__)
app.secret_key = '0d7b8c769c568e41c0eb6d491dee92db'

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Initialize Firebase Admin SDK
def initialize_firebase():
    cred = credentials.Certificate("firebaseauth.json")
    firebase_admin.initialize_app(cred)
    return firestore.client()

db = initialize_firebase()

# Define login_required decorator
def login_required(f):
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login_route'))
        return f(*args, **kwargs)
    return decorated_function

def embed_message(file_path, message, start_bit, periodicity, skip_bits):
    with open(file_path, 'rb+') as file:
        file.seek(skip_bits) 
        data = bytearray(file.read())
        message = bytearray(message.encode())
        message_index = 0
        for i in range(start_bit, len(data) * 8, periodicity):
            if message_index >= len(message):
                break
            byte_index = i // 8
            bit_index = i % 8
            data[byte_index] = (data[byte_index] & ~(1 << bit_index)) | ((message[message_index] & 1) << bit_index)
            message_index += 1
        file.seek(0)
        file.write(data)

def extract_message(file_path, start_bit, periodicity, skip_bits):
    message = bytearray()
    with open(file_path, 'rb') as file:
        file.seek(skip_bits)
        data = bytearray(file.read())
        for i in range(start_bit, len(data) * 8, periodicity):
            byte_index = i // 8
            bit_index = i % 8
            message.append((data[byte_index] >> bit_index) & 1)
    return message

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mov', 'wav'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Login route
@app.route('/', methods=['GET', 'POST'])
def login_route():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_ref = db.collection('users').document(username)
        user_data = user_ref.get()
        if user_data.exists:
            if user_data.to_dict()['password'] == password:
                session['username'] = username
                return redirect('/index')
            else:
                error = 'Invalid username or password'
                return render_template('login.html', error=error)
        else:
            error = 'User does not exist'
            return render_template('login.html', error=error)
    return render_template('login.html')

# Signup route
@app.route('/signup', methods=['GET', 'POST'])
def signup_route():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_ref = db.collection('users').document(username)
        user_data = user_ref.get()
        if user_data.exists:
            error = 'Username already exists'
            return render_template('signup.html', error=error)
        else:
            user_ref.set({
                'username': username,
                'password': password
            })
            session['username'] = username
            return redirect('/index')
    return render_template('signup.html')




# Upload route
@app.route('/upload', methods=['POST'])
def upload():
    if request.method == 'POST':
        file = request.files['file']
        message_text = request.form['message_text']
        message_file = request.files['message_file']
        if message_file:
            message = message_file.read()
        elif message_text:
            message = message_text.encode()
        start_bit = int(request.form['start_bit'])
        periodicity = int(request.form['periodicity'])
        skip_bits = int(request.form['skip_bits'])
        if file.filename == '' or not message:
            return redirect(url_for('index'))
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            embed_message(file_path, message, start_bit, periodicity, skip_bits)
            
            # Generate new filename for embedded file
            embedded_filename = "embedded_" + filename
            embedded_file_path = os.path.join(app.config['UPLOAD_FOLDER'], embedded_filename)
            os.rename(file_path, embedded_file_path)  # Rename the embedded file
            
            # Send the embedded file for download
            return send_file(embedded_file_path, as_attachment=True)
          


# Extract route
@app.route('/extract', methods=['POST'])
def extract_route():
    if request.method == 'POST':
        file = request.files['file']
        periodicity = int(request.form['periodicity'])
        skip_bits = int(request.form['skip_bits']) 
        start_bit = int(request.form['start_bit'])
        if file and allowed_file(file.filename):
            message = extract_message(file, start_bit, periodicity, skip_bits)
            return render_template('extracted_message.html', message=message)
        else:
            return redirect(url_for('index'))
        
# Index route
@app.route('/index')
@login_required
def index():
    return render_template('index.html')

# Success route
@app.route('/success')
def success():
    return 'File submitted successfully!'
        

# Decode route for decoding the embedded file
@app.route('/decode', methods=['GET', 'POST'])
def decode():
    start_bit = 0
    periodicity = 1
    skip_bits = 0
    if request.method == 'POST':
        embedded_file = request.files['file']
        if embedded_file and allowed_file(embedded_file.filename):
            embedded_filename = secure_filename(embedded_file.filename)
            embedded_file_path = os.path.join(app.config['UPLOAD_FOLDER'], embedded_filename)
            embedded_file.save(embedded_file_path)
            # Extract the secret message
            secret_message = extract_message(embedded_file_path, start_bit, periodicity, skip_bits)
            return render_template('decode.html', message=secret_message.decode())
    return render_template('decode.html', message=None)


# Create a route for inputting the embedded file
@app.route('/submit', methods=['GET', 'POST'])  # Changed route to /submit
def submit():
    if request.method == 'POST':
        embedded_file = request.files['file']
        if embedded_file and allowed_file(embedded_file.filename):
            embedded_filename = secure_filename(embedded_file.filename)
            embedded_file_path = os.path.join(app.config['UPLOAD_FOLDER'], embedded_filename)
            embedded_file.save(embedded_file_path)
       
        return send_file(embedded_file_path, as_attachment=True)
        return redirect(url_for('decode', file_path=embedded_file_path))
    else:
        return redirect(url_for('index'))  
      


# Logout route
@app.route('/logout')
def logout_route():
    session.pop('username', None)
    return redirect(url_for('login'))



if __name__ == '__main__':
    app.run(debug=True)
