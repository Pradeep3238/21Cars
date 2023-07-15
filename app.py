from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
from werkzeug.utils import secure_filename
import os


app = Flask(__name__)


app.secret_key = 'your secret key'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'pradeep@3238'
app.config['MYSQL_DB'] = 'pradeep'
app.config['UPLOAD_FOLDER'] = 'uploads'  # Folder to store uploaded images
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif','webp'}

mysql = MySQL(app)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


@app.route('/login', methods =['GET', 'POST'])
def login():
	if 'username' in session:
		return redirect(url_for('home'))
	if request.method == 'POST':
		username=request.form['username']
		password = request.form['password']
		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute('SELECT * FROM accounts WHERE username = % s AND password = % s', (username, password ))
		account = cursor.fetchone()
		if account:
			session['username']=account['username']
			return redirect(url_for('home'))
	else:
		msg = 'Incorrect username / password !'
		return render_template('login.html', msg = msg)
	return render_template('login.html')


@app.route('/logout')

def logout():
	session.pop('loggedin', None)
	session.pop('id', None)
	session.pop('username', None)
	return redirect(url_for('login'))

@app.route('/sign', methods =['GET', 'POST'])
def sign():
	msg = ''
	if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form :
		username = request.form['username']
		password = request.form['password']
		email = request.form['email']
		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute('SELECT * FROM accounts WHERE username = % s', (username, ))
		account = cursor.fetchone()
		if account:
			msg = 'Account already exists !'
		elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
			msg = 'Invalid email address !'
		elif not re.match(r'[A-Za-z0-9]+', username):
			msg = 'Username must contain only characters and numbers !'
		elif not username or not password or not email:
			msg = 'Please fill out the form !'
		else:
			cursor.execute('INSERT INTO accounts VALUES (NULL, % s, % s, % s)', (username, password, email, ))
			mysql.connection.commit()
			return redirect(url_for('login'))
	elif request.method == 'POST':
		msg = 'Please fill out the form !'
	return render_template('sign.html', msg = msg)

@app.route('/location')
def location():
	return render_template("location.html")

@app.route('/about')
def about():
	return render_template("about.html")

@app.route('/contact')
def contact():
	return render_template("contact.html")

@app.route('/',methods=["GET","post"])
def home():
	if 'username' in session:
		username=session['username']
		cursor=mysql.connection.cursor()
		cursor.execute("select * from cardetails")
		posts=cursor.fetchall()
		cursor.close()
		return render_template('home.html',username=username,posts=posts)
	return redirect(url_for('login'))




@app.route('/admin',methods=['GET','POST'])
def admin():
	if request.method == 'POST':
		carname = request.form['carname']
		features= request.form['features']
		ownerdetails=request.form['ownerdetails']
		location=request.form['location']
		 # Handle image upload
		image = request.files['image']
		if image and allowed_file(image.filename):
			filename =secure_filename(image.filename)
			image.save(os.path.join(app.root_path, 'static', 'uploads', filename))
			image_url = os.path.join(app.config['UPLOAD_FOLDER'], filename)
		else:
			image_url = None
		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute('insert into cardetails values(NULL,%s, %s, %s, %s, %s)', (carname,features,ownerdetails,location,image_url ))
		mysql.connection.commit()
		cursor.close()
		return "successs"
	return render_template('admin.html')



@app.route('/booking_details/<car_id>')
def booking_details(car_id):
	cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
	if 'username' in session:
		user_details = session['username'] 
		cursor.execute('SELECT * FROM accounts,cardetails WHERE username = %s and carid=%s', (user_details,car_id))
		user = cursor.fetchone()
		if user:
			cursor.execute("INSERT INTO orders (username, email, carname, features,location,ownerdetails) VALUES (%s, %s, %s, %s,%s,%s)",
                                  (user['username'], user['email'], user['carname'],user['features'],user['location'],user['ownerdetails']))
			mysql.connection.commit()
	cursor.close()
	return render_template('booking_details.html', user=user)

@app.route('/feedback',methods=["get","post"])
def feedback():
	name=request.form['name']
	mobile=request.form['mobile']
	email=request.form['email']
	message=request.form['message']
	cursor=mysql.connection.cursor()
	cursor.execute("Insert into feedback values (%s,%s,%s,%s) ",(name,mobile,email,message))
	mysql.connection.commit()
	cursor.close()
	return "Thanks for your feedback"


@app.route('/admin/feedbacks')
def feedbacks():
	cursor = mysql.connection.cursor()
	cursor.execute("SELECT feedback.name, feedback.mobile, feedback.email, feedback.message FROM feedback INNER JOIN accounts ON feedback.email = accounts.email")
	feedbacks = cursor.fetchall()
	return render_template("feedbacks.html", feedbacks=feedbacks)


@app.route('/admin/orders')
def orders():
	cursor=mysql.connection.cursor()
	cursor.execute('select distinct username,email,carname, ownerdetails from orders')
	orders=cursor.fetchall()
	return render_template('orders.html',orders=orders)

if __name__ == '__app__':
    app.run(debug=True)