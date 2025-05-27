from flask import Flask, render_template, request, redirect, url_for, flash, session
import pymysql
from pymysql.err import IntegrityError
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'



from pymysql.cursors import DictCursor  

db = pymysql.connect(
    host="127.0.0.1",
    user="root",
    password="Cherry@2003",
    db="store",
    
)
cursor = db.cursor()



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/customers', methods=['GET', 'POST'])
def customers():
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        gender = request.form['gender']
        location = request.form['location']
        email = request.form['email']

        try:
            cursor.execute(
                "INSERT INTO customers (name, age, gender, location, email) VALUES (%s, %s, %s, %s, %s)",
                (name, age, gender, location, email)
            )
            db.commit()
            flash("Customer added successfully.", "success")
        except IntegrityError as e:
            if "Duplicate entry" in str(e):
                flash("Customer with this email already exists.", "warning")
            else:
                flash("An error occurred while adding the customer.", "danger")

        return redirect('/customers')

    cursor.execute("SELECT * FROM customers")
    customers = cursor.fetchall()
    return render_template('customer.html', customers=customers)

@app.route('/edit_customer/<email>', methods=['GET', 'POST'])
def edit_customer(email):
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        gender = request.form['gender']
        location = request.form['location']
        cursor.execute("UPDATE customers SET name=%s, age=%s, gender=%s, location=%s WHERE email=%s",
                       (name, age, gender, location, email))
        db.commit()
        flash("Customer updated successfully.")
        return redirect('/customers')

    cursor.execute("SELECT * FROM customers WHERE email = %s", (email,))
    customer = cursor.fetchone()
    return render_template('edit_customer.html', customer=customer)

@app.route('/delete_customer/<email>')
def delete_customer(email):
    cursor.execute("DELETE FROM customers WHERE email = %s", (email,))
    db.commit()
    flash("Customer deleted successfully.")
    return redirect('/customers')


from flask import Flask, render_template, request, redirect, flash
from datetime import datetime

@app.route('/orders', methods=['GET', 'POST'])
def orders():
    if request.method == 'POST':
        customer_email = request.form['customer_email']
        product_category = request.form['product_category']
        product_name = request.form['product_name']
        size = request.form['size']
        price = request.form['price']

        
        cursor.execute("SELECT id FROM customers WHERE email = %s", (customer_email,))
        result = cursor.fetchone()

        if result:
            
            order_date = datetime.today().strftime('%Y-%m-%d')

            customer_id = result[0]
            cursor.execute(
                "INSERT INTO orders (customer_id, product_category, product_name, size, price, order_date) VALUES (%s, %s, %s, %s, %s, %s)",
                (customer_id, product_category, product_name, size, price, order_date)
            )
            db.commit()
            flash("Order added successfully.")
            return redirect('/orders')
        else:
            flash("Customer email not found. Please add the customer first.")
            return redirect('/customers')

   
    cursor.execute("""
    SELECT o.order_id, c.name, o.product_category, o.product_name, o.size, 
           o.price, o.order_date
    FROM orders o
    JOIN customers c ON o.customer_id = c.id
    ORDER BY o.order_id ASC
    """)
    orders = cursor.fetchall()

    cursor.execute("SELECT * FROM customers")
    customers = cursor.fetchall()

    return render_template('order.html', orders=orders, customers=customers)

from datetime import date

@app.route('/edit_order/<int:order_id>', methods=['GET', 'POST'])
def edit_order(order_id):
    if request.method == 'POST':
        product_category = request.form['product_category']
        product_name = request.form['product_name']
        size = request.form['size']
        price = request.form['price']
        order_date = request.form['order_date']

     
        if not order_date:
            order_date = None  

        cursor.execute("""
            UPDATE orders 
            SET product_category=%s, product_name=%s, size=%s, price=%s, order_date=%s 
            WHERE order_id=%s
        """, (product_category, product_name, size, price, order_date, order_id))
        db.commit()
        flash("Order updated successfully.")
        return redirect('/orders')

    
    cursor.execute("""
        SELECT o.order_id, o.customer_id, c.name, o.product_category, o.product_name, o.size, o.price, o.order_date
        FROM orders o JOIN customers c ON o.customer_id = c.id
        WHERE o.order_id = %s
    """, (order_id,))
    order = cursor.fetchone()

    return render_template("edit_order.html", order=order)


@app.route('/delete_order/<int:order_id>')
def delete_order(order_id):
    cursor.execute("DELETE FROM orders WHERE order_id = %s", (order_id,))
    db.commit()
    flash("Order deleted successfully.")
    return redirect('/orders')






@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == "admin" and password == "admin123":
            session['logged_in'] = True
            return redirect('/reports')
        else:
            flash("Invalid credentials. Try again.")
            return redirect('/login')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash("You have been logged out.")
    return redirect('/login')

@app.route('/reports')
def reports():
    if not session.get('logged_in'):
        flash("You must be logged in to view this page.")
        return redirect('/login')
    return render_template('reports.html')  



if __name__ == "__main__":
    app.run(debug=True)


