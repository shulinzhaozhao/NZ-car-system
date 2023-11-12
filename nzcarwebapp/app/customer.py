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

@app.route('/view_customer_profiles')
def view_customer_profiles():
    if not is_authenticated():
        return redirect(url_for('login'))

    # Get the user's role.
    user_role = get_user_role()
    if user_role in ['staff', 'admin']:
        # Retrieve customer profiles from the database (you need to implement this)
        connection = getCursor()
        connection.execute('SELECT * FROM customers LEFT JOIN users on customers.user_id=users.user_id')
        customers = connection.fetchall()

        return render_template('view_customer_profiles.html', customers=customers)
    else:
        return "Unauthorized"

@app.route('/customer/add', methods=['GET', 'POST'])
def add_customer():
    if not is_authenticated():
        return redirect(url_for('login'))

    # Get the user's role.
    user_role = get_user_role()
    if user_role == 'admin':
        msg = ''
        if request.method == 'POST'and 'username' in request.form and 'password' in request.form and 'email' in request.form and 'address' in request.form and 'customer_name' in request.form and 'phone_number' in request.form:
            # Get the customer details from the form submission
            customer_name = request.form['customer_name']
            address = request.form['address']
            email = request.form['email']
            phone_number = request.form['phone_number']
            username = request.form['username']
            password = request.form['password']
            role='customer'
            connection = getCursor()
            connection.execute('SELECT * FROM users WHERE username = %s', (username,))
            account = connection.fetchone()
            connection.execute('SELECT * FROM customers WHERE email = %s', (email,))
            email_entry = connection.fetchone()
            if account:
                msg = 'Account already exists!'
            elif email_entry:
                msg = 'Email already exists!'
            elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
                msg = 'Invalid email address!'
            elif not re.match(r'[A-Za-z0-9]+', username):
                msg = 'Username must contain only characters and numbers!'
            elif not re.match(r'^[A-Za-z0-9\s\-_,./#]+$', address):
                msg = 'Invalid address! The address can contain letters, digits, spaces, and some special characters like -, _, ,, ., /, #.'
            elif not re.match(r'^[A-Za-z\s]+$', customer_name):
                msg = 'Name must contain only letters and spaces!'
            elif not re.match(r'^\+?[0-9]\d{0,14}$', phone_number):
                msg = 'Invalid phone number!'
            elif not username or not password or not email or not address or not customer_name or not phone_number:
                msg = 'Please fill out the form!'
            else:
                # Account doesnt exists and the form data is valid, now insert new account into accounts table
                hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
                print(hashed)
                connection = getCursor()
                connection.execute('INSERT INTO users (username,password,role) VALUES (%s, %s, %s)',(username,hashed,role))
                user_id = connection.lastrowid

                connection = getCursor()        
                connection.execute('INSERT INTO customers (name, address, email, phone_number,user_id) VALUES (%s, %s, %s, %s, %s)', (customer_name, address, email, phone_number,user_id))
                msg = 'You have successfully added a new customer!' 
                return redirect(url_for('view_customer_profiles'))
        elif request.method == 'POST':
            # Form is empty... (no POST data)
            msg = 'Please fill out the form!'

        # If the request method is GET, display the form for adding a new customer
        return render_template('add_customer.html',msg=msg)
    else:
        return "You do not have permission to access this page."
    
@app.route('/customer/<int:customer_id>/edit', methods=['GET', 'POST'])
def edit_customer(customer_id):
    if not is_authenticated():
        return redirect(url_for('login'))

    # Get the user's role.
    user_role = get_user_role()
    if user_role == 'admin':
        msg = ''
        # Fetch the customer details for the specified customer_id from the database
        connection = getCursor()
        connection.execute('SELECT * FROM customers LEFT JOIN users on customers.user_id=users.user_id WHERE customer_id= %s', (customer_id,))
        customer = connection.fetchone()  

        if request.method == 'POST' and 'customer_name' in request.form and 'address' in request.form and 'email' in request.form and 'phone_number' in request.form:
            # Get the customer details from the form submission
            customer_name = request.form['customer_name']
            address = request.form['address']
            email = request.form['email']
            phone_number = request.form['phone_number']
            username = request.form['username']
            password = request.form['password']
            role='customer'
            connection = getCursor()
            connection.execute('SELECT * FROM users WHERE username = %s', (username,))
            account = connection.fetchall()
            user_id=account[0][0]
            connection = getCursor()
            connection.execute('SELECT * FROM customers WHERE email = %s AND customer_id != %s', (email, customer_id))
            email_entry = connection.fetchone()
            connection.execute('SELECT * FROM users LEFT JOIN customers ON customers.user_id=users.user_id WHERE users.user_id = %s AND customer_id != %s', (user_id, customer_id))
            existing_customer = connection.fetchone()
            if existing_customer:
                msg = 'Account already exists!'      
            elif email_entry:
                msg = 'Email already exists!'
            elif not re.match(r'[A-Za-z0-9]+', username):
                msg = 'Username must contain only characters and numbers!'
            elif not re.match(r'^[A-Za-z\s]+$', customer_name):
                msg = 'Name must contain only letters and spaces!'
            elif not re.match(r'^[A-Za-z0-9\s\-_,./#]+$', address):
                msg = 'Invalid address! The address can contain letters, digits, spaces, and some special characters like -, _, ,, ., /, #.'
            elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
                msg = 'Invalid email address!'
            elif not re.match(r'^\+?[0-9]\d{0,14}$', phone_number):
                msg = 'Invalid phone number!'
            else:
                hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
                connection = getCursor()
                connection.execute('UPDATE users SET username=%s,password=%s,role=%s WHERE user_id=%s',(username,hashed,role,user_id))
                connection.execute('UPDATE customers SET name=%s, address=%s, email=%s, phone_number=%s WHERE customer_id=%s',
                                (customer_name, address, email, phone_number, customer_id))
                msg = 'Customer details have been updated successfully.'
                return redirect(url_for('view_customer_profiles'))

        # If the request method is GET, display the form for editing the customer details
        return render_template('edit_customer.html', customer=customer, msg=msg)
    else:
        return "You do not have permission to access this page"


@app.route('/customer/<int:customer_id>/delete', methods=['GET', 'POST'])
def delete_customer(customer_id):
    if not is_authenticated():
        return redirect(url_for('login'))

    # Get the user's role.
    user_role = get_user_role()
    if user_role == 'admin':
        msg = ''
        # Fetch the customer details for the specified customer_id from the database
        connection = getCursor()
        connection.execute('SELECT * FROM customers LEFT JOIN users ON customers.user_id = users.user_id WHERE customers.customer_id = %s',(customer_id,))
        customer = connection.fetchone()
        user_id=customer[5]

        if not customer:
            msg = 'Customer not found.'
        elif request.method == 'POST':
            # Delete the customer from the database
            connection.execute('DELETE FROM customers WHERE customer_id=%s', (customer_id,))
            connection.execute('DELETE FROM users WHERE user_id=%s', (user_id,))
            msg = 'Customer has been deleted successfully.'
            return redirect(url_for('view_customer_profiles'))

        # If the request method is GET, display the confirmation page for deleting the customer
        return render_template('delete_customer.html', customer=customer, msg=msg)
    else:
        return "You do not have permission to access this page."
