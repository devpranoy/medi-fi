from flask import Flask ,render_template, flash, redirect, url_for, session, request, logging
import psycopg2
from functools import wraps
import dbquery
import json

app = Flask(__name__)
def is_logged_in(f):	# Function for implementing security and redirection
	@wraps(f)
	def wrap(*args,**kwargs):
		if 'logged_in' in session:
			return f(*args, **kwargs)
		else:
			flash('Unauthorised, Please Login')
			return redirect(url_for('login'))
	return wrap	# A wrap is a concept that is used to check for authorisation of a request



@app.route('/login', methods=['GET','POST']) #login page
def login():
	if request.method == 'POST':
		error = None
		username = request.form['username']					#GET FORM FIELDS
		password_candidate= request.form['password']	#GET FORM FIELDS
		flag=0
		sql="SELECT password FROM users WHERE username = '%s' "%(username)
		rows = dbquery.fetchone(sql)
		try:				# if no entry found, an error is raised
			for row in rows:
				flag=1
				password=row
			sql="SELECT  id FROM users WHERE username = '%s' "%(username)		#validations
			rows = dbquery.fetchone(sql)
			for row in rows:
				userid=row
			sql="SELECT type FROM users WHERE username= '%s' "%(username)	#validations
			rows = dbquery.fetchone(sql)
			for row in rows:
				type=row
			
			if str(password_candidate) == str(password):	#initialise session variable if passwords match
				session['logged_in'] = True
				session['username'] = str(username)
				session['type']=str(type)
				session['id']=str(userid)
			
                
			else:
				error = 'Username or Password Incorrect'
				return render_template('login.html',error=error)
		except:
			if flag==0:
				error = 'Username or Password Incorrect'
				return render_template('login.html',error=error)


		data = {
		"status": "Success",
        "userID": str(userid),
        "type": str(type),
		"userName": str(username)
    	}
		json_string = json.dumps(data)
		return json_string
	#if verification is successful load the dashboard with session
	return render_template('login.html')
@app.route('/logout')
def logout():
	session.clear()								#Session is destroyed
	flash('You are now logged out','success')
	return redirect(url_for('index'))

@app.route('/signup', methods=['GET','POST'])
def signup():
	if request.method == 'POST':
		message=None
		username = request.form['username']					#GET FORM FIELDS
		password= request.form['password']
		type = request.form['type']
		sql="SELECT id FROM users WHERE username='%s'"%(username) #Security check on username
		try:
			rows = dbquery.fetchone(sql) #if none, error should be raised
			for row in rows:
				f=1
		except:
			sql="INSERT INTO users(username,password,type) VALUES('%s','%s' ,'%s')"%(username,password,type)
			dbquery.inserttodb(sql)	#connecting to db model
			message="User Registration Successful"
			return render_template('signup.html',message=message)
		message="Username Exists"
		return render_template('signup.html',message=message)
	return render_template('signup.html')

@app.route('/', methods=['GET','POST'])
def index():
	return render_template('index.html')

if __name__=='__main__':
	app.secret_key='secret123' #for flash messaging
	app.run(threaded=True,host="localhost",port=80) #Debugger is set to 1 for testing and overriding the default port to http port
