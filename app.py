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
		email = request.form['email']					#GET FORM FIELDS
		password_candidate= request.form['password']	#GET FORM FIELDS
		flag=0
		
		sql="SELECT password FROM users WHERE email = '%s' "%(email)
		rows = dbquery.fetchone(sql)
		try:				# if no entry found, an error is raised
			for row in rows:
				flag=1
				password=row
			sql="SELECT  userno FROM users WHERE email = '%s' "%(email)		#validations
			rows = dbquery.fetchone(sql)
			for row in rows:
				userid=row
			sql="SELECT type FROM users WHERE email= '%s' "%(email)	#validations
			rows = dbquery.fetchone(sql)
			for row in rows:
				type=row
			
			if str(password_candidate) == str(password):	#initialise session variable if passwords match
				session['logged_in'] = True
				session['type']=str(type)
				session['id']=str(userid)
				
				if session['type'] == "Nurse":
					return redirect(url_for('nurse_dash'))
				if session['type'] == "Doctor":
					return redirect(url_for('doctor_dash'))
				if session['type'] == "Patient":
					return redirect(url_for('patient_dash'))
                
			else:
				error = 'Username or Password Incorrect'
				return render_template('login.html',error=error)
		except:
			if flag==0:
				error = 'Username or Password Incorrect'
				return render_template('login.html',error=error)
		
		
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
		email = request.form['email']					#GET FORM FIELDS
		name = request.form['name']
		password= request.form['password']
		type = request.form['type']
		print(name,email,password,type)
		sql="SELECT userno FROM users WHERE email='%s'"%(email) #Security check on username
		try:
			rows = dbquery.fetchone(sql) #if none, error should be raised
			for row in rows:
				f=1
		except:
			sql="INSERT INTO users(name,email,password,type) VALUES('%s','%s' ,'%s','%s')"%(name,email,password,type)
			dbquery.inserttodb(sql)	#connecting to db model
			message="User Registration Successful"
			return render_template('signup.html',message=message)
		message="Email Exists"
		return render_template('signup.html',message=message)
	return render_template('signup.html')

@app.route('/nurse_dash',methods=['GET','POST'])
@is_logged_in						#Can only be accessed if logged in
def nurse_dash():
	#usr=session['userno']	#Recieving the userid for db manipulation from the initilised session
	#sql="SELECT * FROM PROJECTS WHERE USERID = %s"%(usr)
	#projects=dbquery.fetchall(sql)
	return render_template('nurse_dash.html')


@app.route('/doctor_dash',methods=['GET','POST'])
@is_logged_in						#Can only be accessed if logged in
def doctor_dash():
	#usr=session['userno']	#Recieving the userid for db manipulation from the initilised session
	#sql="SELECT * FROM PROJECTS WHERE USERID = %s"%(usr)
	#projects=dbquery.fetchall(sql)
	return render_template('doctor_dash.html')

@app.route('/patient_dash',methods=['GET','POST'])
@is_logged_in						#Can only be accessed if logged in
def patient_dash():
	#usr=session['userno']	#Recieving the userid for db manipulation from the initilised session
	#sql="SELECT * FROM PROJECTS WHERE USERID = %s"%(usr)
	#projects=dbquery.fetchall(sql)
	return render_template('patient_dash.html')

@app.route('/', methods=['GET','POST'])
def index():
	return render_template('index.html')

if __name__=='__main__':
	app.secret_key='secret123' #for flash messaging
	app.run(threaded=True,host="localhost",port=800) #Debugger is set to 1 for testing and overriding the default port to http port
