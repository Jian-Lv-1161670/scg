from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import flash
import re
from datetime import datetime
from datetime import date
from datetime import timedelta
import mysql.connector
from mysql.connector import FieldType
import connect

app = Flask(__name__) 
# Sets the secret key for the Flask application, which is used for securely signing session 
app.secret_key = 'SelwynCampground'

dbconn = None
connection = None

# Establishes a database connection and returns a cursor object.
def getCursor():
    global dbconn
    global connection
    connection = mysql.connector.connect(user=connect.dbuser, \
    password=connect.dbpass, host=connect.dbhost, \
    database=connect.dbname, autocommit=True)
    dbconn = connection.cursor()
    return dbconn

# Establishes a database connection and returns the connection object.
def getCursor1():
    global connection
    connection = mysql.connector.connect(user=connect.dbuser, \
    password=connect.dbpass, host=connect.dbhost, \
    database=connect.dbname, autocommit=True)
    return connection

# Validates an email address using a regular expression.
def validate_email(email):
    email_regex = re.compile(
        r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
    )
    return re.match(email_regex, email) is not None


# Validates a New Zealand phone number using a regular expression.
def validate_phone(phone):
    nz_phone_regex = re.compile(
        r"^(?:\+64|0)?(?:[2345789]\d{7,9})$"
    )
    return re.match(nz_phone_regex, phone) is not None


@app.route("/")
def home():
    connection = getCursor1()
    cursor = connection.cursor()

    # get the total numebr of cusotemrs
    cursor.execute("SELECT COUNT(*) FROM customers")
    customercount = cursor.fetchone()[0]

    # get the lastest customer's info
    cursor.execute("SELECT * FROM customers ORDER BY customer_id DESC LIMIT 1")
    last_customer = cursor.fetchone()
    
    # get today's booking
    cursor.execute("SELECT * FROM bookings WHERE booking_date = CURDATE()")
    bookings = cursor.fetchall()
    booking_count = len(bookings)

    # print the info in terminal for testing purpose
    print("Customer count:", customercount)
    print("Last customer:", last_customer)
    print("Today Bookings:", bookings)
    
    # close connections
    cursor.close()
    connection.close()

    return render_template("index.html", customercount=customercount, last_customer=last_customer, bookings=bookings, booking_count = booking_count, currentdate = datetime.now().date())




@app.route('/campers', methods=['GET', 'POST'])

# Handles the campers route, displaying bookings based on the selected date.
def campers():
    # Get the current date
    currentdate = datetime.now().date()


    if request.method == 'POST':
        # Retrieve the camp date from the form submission
        campdate = request.form.get('campdate')
        
        # If no date is provided, use the current date
        if not campdate:
            campdate = currentdate

        # Establish a new database connection
        connection = getCursor1()
        cursor = connection.cursor()

        # Execute a SQL query to retrieve bookings for the selected date
        cursor.execute("SELECT * FROM bookings JOIN sites ON site = site_id INNER JOIN customers ON customer = customer_id WHERE booking_date = %s;", (campdate,))
        # Fetch all the results from the executed query
        camperList = cursor.fetchall()

        # Close the cursor and connection to the database
        cursor.close()
        connection.close()
        
        # Render the template with the retrieved camper list and the current date
        return render_template("datepickercamper.html", camperlist=camperList, currentdate=currentdate)
    
    # For GET requests, just render the template with the current date
    return render_template('datepickercamper.html', currentdate=currentdate)



@app.route("/booking", methods=['GET','POST'])
# create '/booking' route, allowing users to make a new booking.
def booking():
    if request.method == "GET":
        # Render the date picker template with the current date
        return render_template("datepicker.html", currentdate=datetime.now().date())
    else:
        # Retrieve form data submitted by the user
        bookingNights = request.form.get('bookingnights')
        bookingDate = request.form.get('bookingdate')
        occupancy = request.form.get('occupancy')

        # Convert the booking date from string to date object
        firstNight = date.fromisoformat(bookingDate)
        # Calculate the last night of the booking
        lastNight = firstNight + timedelta(days=int(bookingNights) - 1)

        # Establish a database connection and get a cursor
        connection = getCursor()
        connection.execute("SELECT * FROM customers;")

        # Fetch the list of all customers from the database
        customerList = connection.fetchall()

         # Fetch available sites that can accommodate the specified occupancy and are not booked for the specified date range
        connection.execute("SELECT * FROM sites WHERE occupancy >= %s AND site_id NOT IN (SELECT site FROM bookings WHERE booking_date BETWEEN %s AND %s);", (occupancy, firstNight, lastNight))
        siteList = connection.fetchall()

        # print the received form data for debugging purposes
        print(f"Received form data - bookingNights: {bookingNights}, bookingDate: {bookingDate}, occupancy: {occupancy}")

        # Render the booking form template with the retrieved data
        return render_template("bookingform.html", customerlist=customerList, bookingdate=bookingDate, sitelist=siteList, bookingnights=bookingNights, occupancy=occupancy)


@app.route("/booking/add", methods=['POST'])
# Create '/booking/add' route, allowing users to add a new booking.
def makebooking():
    # Retrieve form data submitted by the user
    bookingNights = request.form.get('bookingnights')
    bookingDate = request.form.get('bookingdate')
    occupancy = request.form.get('occupancy')
    site = request.form.get('site')
    customer = request.form.get('customer')

    # print form data for debugging purposes
    print(f"Received form data - bookingNights: {bookingNights}, bookingDate: {bookingDate}, occupancy: {occupancy}, site: {site}, customer: {customer}")

    # Validate the form data and display appropriate error messages
    if not bookingNights:
        flash('Booking nights cannot be empty!')
    elif not bookingDate:
        flash('Booking date cannot be empty!')
    elif not occupancy:
        flash('Occupancy cannot be empty!')
    elif not site:
        flash('Please select a site!')
    elif not customer:
        flash('Please select a customer!')
    else:
        # Establish a database connection
        connection = getCursor1()
        cursor = connection.cursor()
        
        # Convert the booking date from string to date object
        firstNight = date.fromisoformat(bookingDate)

        # Insert booking data for each night of the stay
        nights = int(bookingNights)
        for i in range(nights):
            booking_date = firstNight + timedelta(days=i)
            print(f"Inserting: site={site}, customer={customer}, booking_date={booking_date}, occupancy={occupancy}, bookingNights={bookingNights}")
            cursor.execute("INSERT INTO bookings (site, customer, booking_date, occupancy) VALUES (%s, %s, %s, %s)", (site, customer, booking_date, occupancy))
       
        # Commit the transaction to the database
        connection.commit()
        print("Booking successful")

        # Close the cursor and connection
        cursor.close()
        connection.close()

        # Flash a success message and redirect to the camper list
        flash('Booking successful!', 'success')
        return redirect(url_for('camperlist'))

    # Redirect back to the form if there is an error
    return redirect(url_for('booking'))
            


@app.route("/customer")
# Create the '/customer' route, displaying a list of customers.
def customerlist():

    # Establish a database connection and get a cursor
    connection = getCursor()

    # Execute a SQL query to retrieve all customers, ordered by customer_id in descending order
    connection.execute("SELECT * FROM customers ORDER BY customer_id DESC;")

    # Fetch all the results from the executed query
    customerlist = connection.fetchall()

    # Print the retrieved customer list for debugging purposes
    print(customerlist)

    # Render the 'customer.html' template with the retrieved customer list
    return render_template("customer.html", customerlist = customerlist)


@app.route("/camperlist")

# Create the '/camperlist' route, displaying a list of campers.
def camperlist():

    # Establish a database connection and get a cursor
    connection = getCursor()

    # Execute a SQL query to retrieve all campers, ordered by customer_id in descending order
    connection.execute("""
    SELECT * 
    FROM bookings
    JOIN sites ON bookings.site = sites.site_id
    JOIN customers ON bookings.customer = customers.customer_id
    ORDER BY booking_id DESC;
""")
    # Fetch all the results from the executed query
    camperlist = connection.fetchall()

    # Print the list for debugging purposes
    print(camperlist)

    # Render the 'camperlist.html' template with the retrieved customer list
    return render_template("camperlist.html", camperlist = camperlist)



@app.route("/new_customer",methods=['GET','POST'])

# Create the '/new_customer' route, allowing users to add a new customer.
def new_customer():
    if request.method == 'POST':
        # Retrieve form data submitted by the user
        firstname = request.form['firstname']
        familyname = request.form['familyname']
        email = request.form['email']
        phone = request.form['phone']
        
        # Validate the form data and display appropriate error messages
        if not firstname:
            flash('First Name Can not be Null')
        elif not familyname:
            flash('Family Name Can not be Null')
        elif not email:
            flash('Email Can not be Null')
        elif not phone:
            flash('Phone number Can not be Null')
        elif not validate_email(email):
            flash('Invalid Email Format')
        elif not validate_phone(phone):
            flash('Invalid Phone Number Format')
        else:

            # Print form data for debugging purposes
            print(f"Inserting: firstname={firstname}, familyname={familyname}, email={email}, phone={phone}")
        
            # Establish a database connection and get a cursor
            connection = getCursor1()
            cursor = connection.cursor()

             # Insert the new customer data into the database
            cursor.execute("INSERT INTO customers (firstname, familyname,email,phone) VALUES (%s, %s, %s, %s)", (firstname,familyname,email,phone))
            
             # Commit the transaction to the database
            connection.commit()

            # Print success message for debugging purposes
            print("Insert successful")

            # Close the cursor and connection
            cursor.close()
            connection.close()

            # Flash a success message and redirect to the home page
            flash('Data successfully inserted!', 'success')
            return redirect(url_for('home'))
        
    # Render the 'new_customer.html' template for GET requests
    return render_template('new_customer.html')


@app.route("/search_customer", methods=['GET', 'POST'])
# Create the '/search_customer' route, allowing users to search for customers.

def search_customer():
    if request.method == "GET":
         # Render the 'search_customer.html' template for GET requests
        return render_template("search_customer.html")
    else:
        # Retrieve the search query from the form data submitted by the user
        search_query = request.form.get('query')

        # Establish a database connection and get a cursor
        connection = getCursor1()
        cursor = connection.cursor()

        # Execute a SQL query to search for customers based on the search query
        cursor.execute("""SELECT * FROM customers WHERE firstname LIKE %s OR familyname LIKE %s OR phone LIKE %s OR email LIKE %s""", ('%' + search_query + '%', '%' + search_query + '%', '%' + search_query + '%', '%' + search_query + '%'))
        customer_list = cursor.fetchall()

        # Print the retrieved customer list for debugging purposes
        print("Customer list:", customer_list)

        # Render the 'search_customer.html' template with the retrieved customer list
        return render_template('search_customer.html', customer_list=customer_list)


@app.route('/customer/<int:customer_id>/delete', methods=['POST'])
# Create the deletion of a customer specified by customer_id.
def delete_customer(customer_id):

    # Establish a database connection and get a cursor
    connection = getCursor1()
    cursor = connection.cursor()

    try:
        # Execute SQL query to delete the customer with the specified customer_id 
        cursor.execute('DELETE FROM customers WHERE customer_id = %s', (customer_id,))
        
        # Commit the transaction to the database
        connection.commit()

        # Flash a success message if the deletion is successful
        flash('Delete Successfully!', 'success')

    except Exception as e:
        # If an error occurs during deletion, rollback the transaction
        connection.rollback()
        # Flash an error message indicating that the customer cannot be deleted
        flash("Error occurred: This customer already made booking, please do not delete this cusotmer!")

    finally:
        # Close the cursor and connection
        cursor.close()
        connection.close()

    # Redirect to the search_customer route after deletion
    return redirect(url_for('search_customer'))
    
    

@app.route('/customer/<int:customer_id>/edit', methods=['GET', 'POST'])

# Handles the editing of customer information specified by customer_id.
def edit_customer(customer_id):

    # Establish a database connection and get a cursor
    connection = getCursor1()
    cursor = connection.cursor()

    if request.method == 'POST':

        # Retrieve form data submitted by the user
        firstname = request.form.get('firstname')
        familyname = request.form.get('familyname')
        email = request.form.get('email')
        phone = request.form.get('phone')

        # Validate the form data and display appropriate error messages
        if not firstname:
            flash('First Name cannot be null', 'error')
        elif not familyname:
            flash('Family Name cannot be null', 'error')
        elif not email:
            flash('Email cannot be null', 'error')
        elif not phone:
            flash('Phone number cannot be null', 'error')
        elif not validate_email(email):
            flash('Invalid Email Format', 'error')
        elif not validate_phone(phone):
            flash('Invalid Phone Number Format', 'error')
        else:
            try:
                # Update customer information in the database
                cursor.execute(
                    "UPDATE customers SET firstname=%s, familyname=%s, email=%s, phone=%s WHERE customer_id=%s",
                    (firstname, familyname, email, phone, customer_id)
                )
                # Commit the transaction to the database
                connection.commit()

                # Flash a success message and redirect to the customer list page
                flash('Information successfully updated!', 'success')
                return redirect(url_for('customer'))
            except Exception as e:

                # If an error occurs, rollback the transaction and flash a message
                connection.rollback()
                flash('Updated')

    # Fetch the customer information from the database for editing
    cursor.execute("SELECT * FROM customers WHERE customer_id = %s", (customer_id,))
    customer = cursor.fetchone()

    # Close the cursor and connection
    cursor.close()
    connection.close()

    # Render the 'edit_customer.html' template with the customer information
    return render_template('edit_customer.html', customer=customer)
    

@app.route('/customer/<int:customer_id>/report', methods=['GET', 'POST'])

# Generates a report for a specific customer including their bookings, total bookings, total occupancy, and average occupancy.
def customer_report(customer_id):

    # Establish a database connection and get a cursor
    connection = getCursor1()
    cursor = connection.cursor()
    # Execute SQL query to retrieve the customer's bookings
    cursor.execute("SELECT * FROM bookings JOIN sites ON site = site_id INNER JOIN customers ON customer = customer_id WHERE customer_id = %s;", (customer_id,))
    customer_report = cursor.fetchall()

    # Execute SQL query to get the total number of bookings for the customer
    cursor.execute("""
        SELECT COUNT(bookings.booking_id) AS total_bookings
        FROM bookings
        JOIN sites ON site = site_id
        INNER JOIN customers ON customer = customer_id
        WHERE customer_id = %s;
    """, (customer_id,))

    total_bookings_result = cursor.fetchone()
    total_bookings = total_bookings_result[0] if total_bookings_result else 0

    if total_bookings > 0:

        # If there are bookings, calculate total and average occupancy
        cursor.execute("""
            SELECT SUM(bookings.occupancy) AS total_occupancy
            FROM bookings
            JOIN sites ON site = site_id
            INNER JOIN customers ON customer = customer_id
            WHERE customer_id = %s;
        """, (customer_id,))
        total_occupancy_result = cursor.fetchone()
        total_occupancy = total_occupancy_result[0] if total_occupancy_result else 0
        average_occupancy = round(total_occupancy / total_bookings, 1)
    else:
        # If there are no bookings, set total and average occupancy to 0
        total_occupancy = 0
        average_occupancy = 0

     # Print the calculated statistics for debugging purposes
    print("Total bookings for customer", customer_id, ":", total_bookings)
    print("Total occupancy for customer", customer_id, ":", total_occupancy)
    print("Average occupancy for customer", customer_id, ":", average_occupancy)

    # Print the customer report for debugging purposes
    print(customer_report)

    # Render the 'customer_report.html' template with the customer report and calculated statistics
    return render_template("customer_report.html", customer_report=customer_report, total_bookings=total_bookings, average_occupancy=average_occupancy, total_occupancy=total_occupancy)

    
if __name__ == "__main__":
    app.run(debug=True)