from flask import Flask, render_template, request, redirect, url_for,session
import mysql.connector
import app.connect as connect
import re
from app import app
import bcrypt
import os
import time
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

@app.route('/view_available_cars')
def view_available_cars():
    # Check if the user is authenticated. If not, redirect to the login page.
    if not is_authenticated():
        return redirect(url_for('login'))

    # Get the user's role.
    user_role = get_user_role()
    connection = getCursor()
    connection.execute('SELECT * FROM rentalcars where availability=1')
    available_rental_cars = connection.fetchall()
    print(user_role)
    # Check if the user's role is allowed to access this page.
    if user_role in [ 'customer', 'staff', 'admin']:
        return render_template('available_rental_cars.html', available_rental_cars=available_rental_cars)

    else:
        return "You do not have permission to access this page."

@app.route('/view_all_cars')
def view_all_cars():
    # Check if the user is authenticated. If not, redirect to the login page.
    if not is_authenticated():
        return redirect(url_for('login'))

    # Get the user's role.
    user_role = get_user_role()
    connection = getCursor()
    connection.execute('SELECT * FROM rentalcars')
    all_rental_cars = connection.fetchall()

    # Check if the user's role is allowed to access this page.    
    if user_role == 'staff'or user_role == 'admin':
        return render_template('view_all_cars.html', all_rental_cars=all_rental_cars)
    else:
        return "You do not have permission to access this page."
    
@app.route('/car/<int:car_id>')
def car_details(car_id):
    if not is_authenticated():
        return redirect(url_for('login'))

    # Get the user's role.
    user_role = get_user_role()

    connection = getCursor()
    connection.execute('SELECT * FROM rentalcars where car_id=%s', (car_id,))
    car_details = connection.fetchone()

    # Check if the user's role is allowed to access this page.
    if user_role in [ 'customer', 'staff', 'admin']:
        return render_template('car_details.html', car_details=car_details)
    else:
        return "You do not have permission to access this page."

@app.route('/car/add', methods=['GET', 'POST'])
def add_car():
    if not is_authenticated():
        return redirect(url_for('login'))
    user_role = get_user_role()
    
    if user_role in ['admin', 'staff']:
        msg = ''
        if request.method == 'POST'and 'car_model' in request.form and 'registration_number' in request.form and 'year' in request.form and 'seating_capacity' in request.form and 'rental_per_day' in request.form: 
            # Get the car details from the form submission
            car_model = request.form['car_model']
            registration_number = request.form['registration_number']
            year = request.form['year']
            seating_capacity = request.form['seating_capacity']
            rental_per_day = request.form['rental_per_day']
            car_image = request.files['car_image']  # Assuming you use a file input for the car image
            # Check if registration_number exists using MySQL
            connection = getCursor()
            connection.execute('SELECT * FROM rentalcars WHERE registration_number = %s', (registration_number,))
            car = connection.fetchone()

            if car:
                msg = 'This Car already exists!'
            elif not re.match(r'^[A-Za-z0-9\s!@#$%^&*()_+{}|:"<>?`\-=[\];\',./\\]*$', car_model):
                msg = 'Car model must contain only letters, numbers, and common special characters.'
            elif not re.match(r'^[A-Za-z0-9\s\-]+$', registration_number):
                msg = 'Invalid registration number. It can contain letters, numbers, spaces, and hyphens.'
            elif not year.isdigit() or not (1900 <= int(year) <= 2023):
                msg = 'Year must be a number between 1900 and 2023.'
            elif not seating_capacity.isdigit() or not (2 <= int(seating_capacity) <= 10):
                msg = 'Seating capacity must be a number between 2 and 10.'
            elif not rental_per_day.replace('.', '', 1).isdigit() or float(rental_per_day) <= 0:
                msg = 'Rental per day must be a positive number.'

            elif not car_model or not registration_number or not year or not seating_capacity or not rental_per_day:
                msg = 'Please fill out the form!'
            else:
                # Read the image file as binary data
                current_path = os.path.abspath(__file__)
                current_dir = os.path.dirname(current_path)
                file_name = str(time.time()) + car_image.filename
                car_image.save(current_dir+"/static/images/"+file_name)
                connection = getCursor()
                connection.execute('INSERT INTO rentalcars (car_model,registration_number,year,seating_capacity,rental_per_day,car_image, availability) VALUES (%s,%s,%s,%s,%s,%s,1)',(car_model,registration_number,year,seating_capacity,rental_per_day,file_name))
                msg = 'New car has been successfully added!'
                return redirect(url_for('view_all_cars'))
    else:
        return "You do not have permission to access this page."
    # If the request method is GET, display the form for adding a new car
    return render_template('add_car.html',msg=msg)

@app.route('/car/<int:car_id>/edit', methods=['GET', 'POST'])
def edit_car(car_id):
    if not is_authenticated():
        return redirect(url_for('login'))
    user_role = get_user_role()  
    if user_role in ['admin', 'staff']:
        msg = ''
        connection = getCursor()
        connection.execute('SELECT * FROM rentalcars WHERE car_id = %s', (car_id,))
        car_details = connection.fetchone()   
        if request.method == 'POST':
        # Get the updated car details from the form submission
            car_model = request.form['car_model']
            registration_number = request.form['registration_number']
            year = request.form['year']
            seating_capacity = request.form['seating_capacity']
            rental_per_day = request.form['rental_per_day']
            car_image = request.files['car_image']
            file_name = car_details[7]
            is_available = 1 if request.form.get('is_available') == 'on' else 0
            connection = getCursor()
            connection.execute('SELECT * FROM rentalcars WHERE registration_number = %s AND car_id != %s', (registration_number,car_id))
            existing_car = connection.fetchone()
            if existing_car:
                msg = 'Car exist'
            elif not re.match(r'^[A-Za-z0-9\s!@#$%^&*()_+{}|:"<>?`\-=[\];\',./\\]*$', car_model):
                msg = 'Car model must contain only letters, numbers, and common special characters.'
            elif not re.match(r'^[A-Za-z0-9\s\-]+$', registration_number):
                msg = 'Invalid registration number. It can contain letters, numbers, spaces, and hyphens.'
            elif not year.isdigit() or not (1900 <= int(year) <= 2023):
                msg = 'Year must be a number between 1900 and 2023.'
            elif not seating_capacity.isdigit() or not (2 <= int(seating_capacity) <= 10):
                msg = 'Seating capacity must be a number between 2 and 10.'
            elif not rental_per_day.replace('.', '', 1).isdigit() or float(rental_per_day) <= 0:
                msg = 'Rental per day must be a positive number.'

            elif not car_model or not registration_number or not year or not seating_capacity or not rental_per_day:
                msg = 'Please fill out the form!'
            if msg:
                return render_template('edit_car.html', car_details=car_details,msg=msg)

            if 'car_image' in request.files and request.files['car_image'].filename:
                car_image = request.files['car_image']
                current_path = os.path.abspath(__file__)
                current_dir = os.path.dirname(current_path)
                new_file_name = str(time.time()) + car_image.filename
                car_image.save(current_dir+"/static/images/"+new_file_name)
                file_name = new_file_name
                
            # Update the car details in the database
            connection = getCursor()
            connection.execute('UPDATE rentalcars SET car_model = %s, registration_number = %s, year = %s, seating_capacity = %s, rental_per_day = %s, availability = %s,car_image = %s WHERE car_id = %s',
                            (car_model, registration_number, year, seating_capacity, rental_per_day,is_available,file_name, car_id))
            msg = 'Car details have been edited successfully.'
            return redirect(url_for('view_all_cars'))
       
        return render_template('edit_car.html', car_details=car_details,msg=msg)
    else:
        return "You do not have permission to access this page."

@app.route('/car/<int:car_id>/delete', methods=['GET', 'POST'])
def delete_car(car_id):
    if not is_authenticated():
        return redirect(url_for('login'))
    user_role = get_user_role()
    
    if user_role in ['admin', 'staff']:
        connection = getCursor()
        if request.method == 'POST':
            # Delete the car from the database
            connection.execute('DELETE FROM rentalcars WHERE car_id = %s', (car_id,))
            return redirect(url_for('view_all_cars'))

        # Fetch the car details for the specified car_id from the database
        connection.execute('SELECT * FROM rentalcars WHERE car_id = %s', (car_id,))
        car_details = connection.fetchone()

        if car_details is None:
            # If the car with the specified car_id is not found, you can handle it accordingly (e.g., show an error message)
            return "Car not found."
    else:
        return "Unauthorized"
    # Display a confirmation page asking the user to confirm the deletion
    return render_template('delete_car.html', car_details=car_details)