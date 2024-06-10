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
app.secret_key = 'SelwynCampground'

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

def getCursor1():
    global connection
    connection = mysql.connector.connect(user=connect.dbuser, \
    password=connect.dbpass, host=connect.dbhost, \
    database=connect.dbname, autocommit=True)
    return connection

def validate_email(email):
    # 
    return '@' in email

def validate_phone(phone):
    # 
    return len(phone) >= 8 and len(phone) <= 15 and phone.isdigit()


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
def campers():
    currentdate = datetime.now().date()

    if request.method == 'POST':
        campdate = request.form.get('campdate')
        
        if not campdate:
            campdate = currentdate

        connection = getCursor1()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM bookings JOIN sites ON site = site_id INNER JOIN customers ON customer = customer_id WHERE booking_date = %s;", (campdate,))
        camperList = cursor.fetchall()

        cursor.close()
        connection.close()
        
        return render_template("datepickercamper.html", camperlist=camperList, currentdate=currentdate)
    return render_template('datepickercamper.html', currentdate=currentdate)



@app.route("/booking", methods=['GET','POST'])
def booking():
    if request.method == "GET":
        return render_template("datepicker.html", currentdate = datetime.now().date())
    else:
        bookingNights = request.form.get('bookingnights')
        bookingDate = request.form.get('bookingdate')
        occupancy = request.form.get('occupancy')
        firstNight = date.fromisoformat(bookingDate)

        lastNight = firstNight + timedelta(days=int(bookingNights))
        connection = getCursor()
        connection.execute("SELECT * FROM customers;")
        customerList = connection.fetchall()
        connection.execute("select * from sites where occupancy >= %s AND site_id not in (select site from bookings where booking_date between %s AND %s);",(occupancy,firstNight,lastNight))
        siteList = connection.fetchall()
        
        print(f"Received form data - bookingNights: {bookingNights}, bookingDate: {bookingDate}, occupancy: {occupancy}")
        return render_template("bookingform.html", customerlist = customerList, bookingdate=bookingDate, sitelist = siteList, bookingnights = bookingNights, occupancy = occupancy)    



@app.route("/booking/add", methods=['POST'])


def makebooking():
    bookingNights = request.form.get('bookingnights')
    bookingDate = request.form.get('bookingdate')
    occupancy = request.form.get('occupancy')
    site = request.form.get('site')
    customer = request.form.get('customer')

    # Debugging: print received form data
    print(f"Received form data - bookingNights: {bookingNights}, bookingDate: {bookingDate}, occupancy: {occupancy}, site: {site}, customer: {customer}")

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
        firstNight = date.fromisoformat(bookingDate)
        print(f"Inserting: bookingNights={bookingNights}, bookingDate={bookingDate}, occupancy={occupancy}, site={site}, customer={customer}")
        connection = getCursor1()
        cursor = connection.cursor()
        cursor.execute("INSERT INTO bookings (site, customer, booking_date, occupancy, booking_night) VALUES (%s, %s, %s, %s, %s)", (site, customer, firstNight, occupancy, bookingNights))
        connection.commit()
        print("Booking successful")

        cursor.close()
        connection.close()
        flash('Booking successful !', 'success')
        return redirect(url_for('camperlist'))

    # Redirect back to the form if there is an error
    return redirect(url_for('booking'))

def is_booking_overlapping(site, booking_date, booking_nights):
    # 
    lastNight = booking_date + timedelta(days=booking_nights)
    
    # 
    connection = getCursor1()
    cursor = connection.cursor()
    cursor.execute("""
        SELECT COUNT(*) FROM bookings
        WHERE site = %s
        AND booking_date <= %s
        AND booking_date + INTERVAL booking_nights DAY >= %s
    """, (site, lastNight, booking_date))
    overlapping_count = cursor.fetchone()[0]
    
    cursor.close()
    connection.close()
    
    # 
    return overlapping_count > 0
    

        


@app.route("/customer")
def customerlist():
    connection = getCursor()
    connection.execute("SELECT * FROM customers ORDER BY customer_id DESC;")
    customerlist = connection.fetchall()
    print(customerlist)
    return render_template("customer.html", customerlist = customerlist)


@app.route("/camperlist")
def camperlist():
    connection = getCursor()
    connection.execute("""
    SELECT * 
    FROM bookings
    JOIN sites ON bookings.site = sites.site_id
    JOIN customers ON bookings.customer = customers.customer_id
    ORDER BY booking_id DESC;
""")
    camperlist = connection.fetchall()

    print(camperlist)
    return render_template("camperlist.html", camperlist = camperlist)




@app.route("/new_customer",methods=['GET','POST'])
def new_customer():
    if request.method == 'POST':
        firstname = request.form['firstname']
        familyname = request.form['familyname']
        email = request.form['email']
        phone = request.form['phone']
        
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
        # 
            print(f"Inserting: firstname={firstname}, familyname={familyname}, email={email}, phone={phone}")
        
            connection = getCursor1()
            cursor = connection.cursor()

            cursor.execute("INSERT INTO customers (firstname, familyname,email,phone) VALUES (%s, %s, %s, %s)", (firstname,familyname,email,phone))
            connection.commit()

            print("Insert successful")

            cursor.close()
            connection.close()
            flash('Data successfully inserted!', 'success')
            return redirect(url_for('home'))
    
    return render_template('new_customer.html')


@app.route("/search_customer", methods=['GET', 'POST'])
def search_customer():
    if request.method == "GET":
        return render_template("search_customer.html")
    else:
        search_query = request.form.get('query')

        connection = getCursor1()
        cursor = connection.cursor()
        cursor.execute("""SELECT * FROM customers WHERE firstname LIKE %s OR familyname LIKE %s OR phone LIKE %s OR email LIKE %s""", ('%' + search_query + '%', '%' + search_query + '%', '%' + search_query + '%', '%' + search_query + '%'))
        customer_list = cursor.fetchall()

        # 打印从数据库中获取的客户列表
        print("Customer list:", customer_list)
        return render_template('search_customer.html', customer_list=customer_list)


@app.route('/customer/<int:customer_id>/delete', methods=['POST'])
def delete_customer(customer_id):
    connection = getCursor1()
    cursor = connection.cursor()

    # 执行删除SQL语句
    cursor.execute('DELETE FROM customers WHERE customer_id = %s', (customer_id,))
    connection.commit()

    cursor.close()
    connection.close()

    flash('删除成功！', 'success')

    return redirect(url_for('search_customer'))
    
    

@app.route('/customer/<int:customer_id>/edit', methods=['GET', 'POST'])
def edit_customer(customer_id):
    connection = getCursor1()
    cursor = connection.cursor()

    if request.method == 'POST':
        firstname = request.form.get('firstname')
        familyname = request.form.get('familyname')
        email = request.form.get('email')
        phone = request.form.get('phone')

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
                cursor.execute(
                    "UPDATE customers SET firstname=%s, familyname=%s, email=%s, phone=%s WHERE customer_id=%s",
                    (firstname, familyname, email, phone, customer_id)
                )
                connection.commit()
                flash('Information successfully updated!', 'success')
                return redirect(url_for('customer'))
            except Exception as e:
                connection.rollback()
                flash('Update failed: ' + str(e), 'error')
    
    cursor.execute("SELECT * FROM customers WHERE customer_id = %s", (customer_id,))
    customer = cursor.fetchone()

    cursor.close()
    connection.close()

    return render_template('edit_customer.html', customer=customer)
    
    
    
if __name__ == "__main__":
    app.run(debug=True)