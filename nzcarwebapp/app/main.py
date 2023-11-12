from flask import Flask, render_template, request, redirect, url_for,session
import mysql.connector
import app.connect as connect
import re
from app import app
import bcrypt
app.secret_key = 'your secret key'
dbconn = None
connection = None

def getCursor():
    global dbconn
    global connection
    connection = mysql.connector.connect(user=connect.dbuser, \
    password=connect.dbpass, host=connect.dbhost, \
    database=connect.dbname, autocommit=True)
    dbconn = connection.cursor()
    return dbconn

def is_authenticated():
    return 'role' in session

def get_user_role():
    # In a real application, you would likely retrieve the user's role from a database.
    # For this example, let's assume a user with the username 'admin' has the role 'admin'.
    if 'role' in session:
        if session['role'] == 'admin':
            return 'admin'
        elif session['role'] == 'customer':
            return 'customer'
        elif session['role'] == 'staff':
            return 'staff'
    return None

@app.route('/')
def index():
    return render_template('login.html')

# http://localhost:5000/login/ - this will be the login page, we need to use both GET and POST requests
@app.route('/login', methods=['GET', 'POST'])
def login():
# Output message if something goes wrong...
    msg = ''      
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        user_password = request.form['password']
        # Check if account exists using MySQL
        connection = getCursor()
        connection.execute('SELECT * FROM users WHERE username = %s', (username,))
        # Fetch one record and return result
        account = connection.fetchone()
        if account is not None:
            password = account[2]
            role = account[3] 
            if bcrypt.checkpw(user_password.encode('utf-8'),password.encode('utf-8')):  
            # If account exists in accounts table in out database
            # Create session data, we can access this data in other routes
                session['loggedin'] = True
                session['id'] = account[0]
                session['username'] = account[1]
                session['role'] = account[3]
                print(session['role'] ) 
                # Redirect to home page
                if session['role'] == 'admin':
                    return redirect(url_for('admin'))
                elif session['role'] == 'customer':
                    return redirect(url_for('customer'))
                elif session['role'] == 'staff':
                    return redirect(url_for('staff'))
                else:
                    # Account exists, but the role is not defined. Redirect to home page or handle the scenario accordingly.
                    return redirect(url_for('home'))
            
            else:
                #password incorrect
                msg = 'Incorrect password!'
        else:
                # Account doesnt exist or username incorrect
            msg = 'Account doesnt exist or username incorrect'
    # Show the login form with message (if any)
    return render_template('login.html', msg=msg)



@app.route('/home')
def home():
    # Your home page logic here
    return render_template('home.html')

@app.route('/protected')
def protected():
    # Check if the user is authenticated. If not, redirect to the login page.
    if not is_authenticated():
        return redirect(url_for('login'))

    # Get the user's role.
    user_role = get_user_role()

    # Check if the user's role is allowed to access this page.
    if user_role in ['admin', 'member', 'staff']:
        return f"This is a protected page for {user_role}, {session['username']}! <a href='/logout'>Logout</a>"
    else:
        return "Unauthorized"


@app.route('/admin')
def admin():
    # Check if the user is authenticated. If not, redirect to the login page.
    if not is_authenticated():
        return redirect(url_for('login'))

    # Get the user's role.
    user_role = get_user_role()

    # Check if the user's role is allowed to access this page.
    if user_role == 'admin':
        return render_template("home_admin.html")
    else:
        return "Unauthorized"
    
@app.route('/customer')
def customer():
    # Check if the user is authenticated. If not, redirect to the login page.
    if not is_authenticated():
        return redirect(url_for('login'))

    # Get the user's role.
    user_role = get_user_role()

    # Check if the user's role is allowed to access this page.
    if user_role == 'customer':
        return render_template("home_customer.html")
    else:
        return "Unauthorized"

@app.route('/staff')
def staff():
    # Check if the user is authenticated. If not, redirect to the login page.
    if not is_authenticated():
        return redirect(url_for('login'))

    # Get the user's role.
    user_role = get_user_role()
    # Check if the user's role is allowed to access this page.
    if user_role == 'staff':
        return render_template("home_staff.html")
    else:
        return "Unauthorized"

@app.route('/logout') # http://localhost:5000/logout - this will be the logout page
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   session.pop('role', None)
   # Redirect to login page
   return redirect(url_for('login'))

# http://localhost:5000/register - this will be the registration page, we need to use both GET and POST requests
@app.route('/register', methods=['GET', 'POST'])
def register():
# Output message if something goes wrong...
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form and 'address' in request.form and 'name' in request.form and 'phone_number' in request.form and 'role' in request.form:
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        address = request.form['address']
        name = request.form['name']
        phone_number = request.form['phone_number']
        role = request.form['role']
        # Check if account exists using MySQL
        connection = getCursor()
        connection.execute('SELECT * FROM users WHERE username = %s', (username,))
        account = connection.fetchone()
        # If account exists show error and validation checks
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not re.match(r'^[A-Za-z0-9\s\-_,./#]+$', address):
            msg = 'Invalid address! The address can contain letters, digits, spaces, and some special characters like -, _, ,, ., /, #.'
        elif not re.match(r'^[A-Za-z\s]+$', name):
            msg = 'Name must contain only letters and spaces!'
        elif not re.match(r'^\+?[0-9]\d{0,14}$', phone_number):
            msg = 'Invalid phone number!'

        elif not username or not password or not email or not address or not name or not phone_number or not role:
            msg = 'Please fill out the form!'
        else:
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            print(hashed)
            connection = getCursor()
            connection.execute('INSERT INTO users (username,password,role) VALUES (%s, %s, %s)',(username,hashed,role))
            user_id = connection.lastrowid
            if role == "customer":   
                connection = getCursor()        
                connection.execute('INSERT INTO customers (name, address, email, phone_number,user_id) VALUES (%s, %s, %s, %s, %s)', (name, address, email, phone_number,user_id))
            elif role == "admin" or role =='staff':  
                connection = getCursor()
                connection.execute('INSERT INTO staff (name, address, email, phone_number,user_id) VALUES (%s, %s, %s, %s, %s)', (name, address, email, phone_number,user_id))
                msg = 'You have successfully registered!' 
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('register.html', msg=msg)


# http://localhost:5000/profile - this will be the profile page, only accessible for loggedin users
@app.route('/profile')
def profile():
    # Check if user is loggedin
    
    if 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
        role=session['role']
        if role == 'customer':
            connection = getCursor()
            connection.execute('SELECT * FROM customers LEFT JOIN users on customers.user_id=users.user_id WHERE users.user_id = %s ', (session['id'],))
            account = connection.fetchone()
            return render_template('profile.html', account=account)
        if role == 'admin' or role == 'staff':
            connection = getCursor()
            connection.execute('SELECT * FROM staff LEFT JOIN users on staff.user_id=users.user_id WHERE users.user_id = %s ', (session['id'],))
            account = connection.fetchone()
            # Show the profile page with account info
            return render_template('profile.html', account=account)
      
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

@app.route('/profile/update', methods=['GET', 'POST'])
def update_profile():
    # Check if user is loggedin

    role = session['role']
    # Retrieve the user's current profile information from the database
    connection = getCursor()
    if role == 'customer':
        connection.execute('SELECT * FROM customers LEFT JOIN users ON customers.user_id = users.user_id WHERE users.user_id = %s', (session['id'],))
    elif role in ['admin', 'staff']:
        connection.execute('SELECT * FROM staff LEFT JOIN users ON staff.user_id = users.user_id WHERE users.user_id = %s', (session['id'],))
    account = connection.fetchone()
    user_id=account[5]
    msg=''
    if request.method == 'POST' and 'password' in request.form and 'email' in request.form and 'address' in request.form and 'name' in request.form and 'phone_number' in request.form and 'username' in request.form:
        password = request.form['password']
        email = request.form['email']
        address = request.form['address']
        name = request.form['name']
        phone_number = request.form['phone_number']
        username=request.form['username']
        if role == "customer":  
            connection = getCursor()
            connection.execute('SELECT * FROM users LEFT JOIN customers ON customers.user_id = users.user_id WHERE customers.email = %s AND users.user_id != %s', (email, user_id))
            email_entry = connection.fetchone()
            connection.execute('SELECT * FROM users LEFT JOIN customers ON customers.user_id = users.user_id WHERE users.username = %s AND users.user_id != %s', (username,user_id))
            existing_user = connection.fetchone()
            # If account exists show error and validation checks
            if existing_user:
                msg = 'Account already exists!'      
            elif email_entry:
                msg = 'Email already exists!'
            elif not re.match(r'^[A-Za-z\s]+$', name):
                msg = 'Name must contain only letters and spaces!'
            elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
                msg = 'Invalid email address!'
            elif not re.match(r'^[A-Za-z0-9\s\-_,./#]+$', address):
                msg = 'Invalid address! The address can contain letters, digits, spaces, and some special characters like -, _, ,, ., /, #.'  
            elif not re.match(r'^\+?[0-9]\d{0,14}$', phone_number):
                msg = 'Invalid phone number!'
            elif not re.match(r'[A-Za-z0-9]+', username):
                msg = 'Username must contain only characters and numbers!'
            elif not password or not email or not address or not name or not phone_number:
                msg = 'Please fill out the form!'
            else :
                # Account doesnt exists and the form data is valid, now insert new account into accounts table
                hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
                connection = getCursor()
                connection.execute('UPDATE users SET username=%s, password=%s, role=%s WHERE user_id=%s ',(username,hashed,role,session['id']))
                connection = getCursor()        
                connection.execute('UPDATE customers SET name=%s, address=%s, email=%s, phone_number=%s WHERE user_id=%s', (name, address, email, phone_number,session['id']))
                msg = 'Profile updated successfully!'

        elif role == "admin" or role =='staff':  
            connection = getCursor()
            connection.execute('SELECT * FROM users LEFT JOIN staff ON staff.user_id = users.user_id WHERE staff.email = %s AND users.user_id != %s', (email, user_id))
            email_entry = connection.fetchone()
            connection.execute('SELECT * FROM users LEFT JOIN staff ON staff.user_id = users.user_id WHERE users.username = %s AND users.user_id != %s', (username,user_id))
            existing_user = connection.fetchone()

            # If account exists show error and validation checks
            if existing_user:
                msg = 'Account already exists!'      
            elif email_entry:
                msg = 'Email already exists!'
            elif not re.match(r'^[A-Za-z\s]+$', name):
                msg = 'Name must contain only letters and spaces!'
            elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
                msg = 'Invalid email address!'
            elif not re.match(r'^[A-Za-z0-9\s\-_,./#]+$', address):
                msg = 'Invalid address! The address can contain letters, digits, spaces, and some special characters like -, _, ,, ., /, #.'    
            elif not re.match(r'^\+?[0-9]\d{0,14}$', phone_number):
                msg = 'Invalid phone number!'
            elif not re.match(r'[A-Za-z0-9]+', username):
                msg = 'Username must contain only characters and numbers!'
            elif not password or not email or not address or not name or not phone_number:
                msg = 'Please fill out the form!'
            else :
                # Account doesnt exists and the form data is valid, now insert new account into accounts table
                hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
                connection = getCursor()
                connection.execute('UPDATE users SET username=%s, password=%s, role=%s WHERE user_id=%s ',(username,hashed,role,session['id']))
                connection = getCursor()
                connection.execute('UPDATE staff SET name=%s, address=%s, email=%s, phone_number=%s WHERE user_id=%s', (name, address, email, phone_number,session['id']))

                # Show a success message
                msg = 'Profile updated successfully!'

        if role == 'customer':
            connection.execute('SELECT * FROM customers LEFT JOIN users ON customers.user_id = users.user_id WHERE users.user_id = %s', (session['id'],))
        elif role in ['admin', 'staff']:
            connection.execute('SELECT * FROM staff LEFT JOIN users ON staff.user_id = users.user_id WHERE users.user_id = %s', (session['id'],))
        account = connection.fetchone()
        return render_template('profile_update.html', account=account, msg=msg)
    # Show the profile update form
    return render_template('profile_update.html', account=account)
