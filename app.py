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

    # 获取客户总数
    cursor.execute("SELECT COUNT(*) FROM customers")
    customercount = cursor.fetchone()[0]

    # 获取最新的客户，假设主键列名为 `customer_id`
    cursor.execute("SELECT * FROM customers ORDER BY customer_id DESC LIMIT 1")
    last_customer = cursor.fetchone()
    
    # 获取今天的预订
    cursor.execute("SELECT * FROM bookings WHERE booking_date = CURDATE()")
    bookings = cursor.fetchall()
    booking_count = len(bookings)

    # 打印调试信息
    print("Customer count:", customercount)
    print("Last customer:", last_customer)
    print("Today Bookings:", bookings)
    
    # 关闭数据库连接
    cursor.close()
    connection.close()

    return render_template("index.html", customercount=customercount, last_customer=last_customer, bookings=bookings, booking_count = booking_count, currentdate = datetime.now().date())


    



@app.route("/campers", methods=['GET','POST'])
def campers():
    if request.method == "GET":
        return render_template("datepickercamper.html", currentdate = datetime.now().date())
    else:
        campDate = request.form.get('campdate')
        connection = getCursor()
        connection.execute("SELECT * FROM bookings join sites on site = site_id inner join customers on customer = customer_id where booking_date= %s;",(campDate,))
        camperList = connection.fetchall()
        return render_template("datepickercamper.html", camperlist = camperList)


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
        return render_template("bookingform.html", customerlist = customerList, bookingdate=bookingDate, sitelist = siteList, bookingnights = bookingNights)    



@app.route("/booking/add", methods=['POST'])
def makebooking():
    print(request.form)
    pass


@app.route("/customer")
def customerlist():
    connection = getCursor()
    connection.execute("SELECT * FROM customers ORDER BY customer_id DESC;")
    customerlist = connection.fetchall()
    print(customerlist)
    return render_template("customer.html", customerlist = customerlist)



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
    
    










if __name__ == "__main__":
    app.run(debug=True)