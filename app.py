from flask import Flask ,render_template, flash, redirect, url_for, session, request, logging
import psycopg2
from functools import wraps
import dbquery
import json
import os
from werkzeug import secure_filename
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
				session['email']=email
				
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
	sql="SELECT * FROM patient WHERE nurseid = '%s'"%(session['id'])
	info=dbquery.fetchall(sql)
	return render_template('nurse_dash.html',info=info)


@app.route('/doctor_dash',methods=['GET','POST'])
@is_logged_in						#Can only be accessed if logged in
def doctor_dash():
	email=session['email']	#Recieving the userid for db manipulation from the initilised session

	sql = "Select * from appointment where doctoremail = '%s'"%(email)
	appointments=dbquery.fetchall(sql)
	
	return render_template('doctor_dash.html',appointments = appointments)

@app.route('/medibot',methods=['GET','POST'])
@is_logged_in						#Can only be accessed if logged in
def medibot():
	if request.method == 'POST':
		try:
			slot = request.form['slot']
			print(slot)
			
			medicine = request.form['medicine']
			sql="INSERT INTO medibot(medicine,slot) VALUES('%s','%s' )"%(medicine,slot)
			dbquery.inserttodb(sql)	#connecting to db model
			bashCommand = "curl -v -F slot=%s 192.168.43.112:80"%(slot)
			import subprocess
			process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
		
			
		except:
			dispense = request.form['dispense']
			print(dispense)
			sql = "select * from medibot where medicine ='%s'"%(dispense)
			slotinfo = dbquery.fetchall(sql)
			slot = slotinfo[0][1]
			bashCommand = "curl -v -F slot=%s 192.168.43.112:80"%(slot)
			import subprocess
			process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
			sql ="delete from medibot where slot ='%s'"%(slot)
			dbquery.inserttodb(sql)
	sql = "select * from medicine"
	medicines = dbquery.fetchall(sql)
	sql = "select * from medibot"
	medicinebots = dbquery.fetchall(sql)
	return render_template('medibot.html',medicines = medicines, medicinebots = medicinebots)
	


@app.route('/patient_dash',methods=['GET','POST'])
@is_logged_in						#Can only be accessed if logged in
def patient_dash():
	#usr=session['userno']	#Recieving the userid for db manipulation from the initilised session
	#sql="SELECT * FROM PROJECTS WHERE USERID = %s"%(usr)
	#projects=dbquery.fetchall(sql)
	if request.method=='POST':
		title = request.form['title']
		remark = request.form['remark']
		app.config['UPLOAD_FOLDER']="/Users/pranoy/Desktop/medi-fi/static/uploads/%s"%(session['email'])
		if not os.path.exists(app.config['UPLOAD_FOLDER']):
			os.makedirs(app.config['UPLOAD_FOLDER'])
		try:
			f = request.files['file']
			f.save(os.path.join(app.config['UPLOAD_FOLDER'],f.filename))
			print(f.filename)
			sql="INSERT INTO posts(email,title,remark,image,post_by) VALUES('%s','%s' ,'%s','%s','%s')"%(email,title,remark,f.filename,session['id'])
			dbquery.inserttodb(sql)

		except:
			sql="INSERT INTO posts(email,title,remark,post_by) VALUES('%s','%s' ,'%s','%s')"%(email,title,remark,session['id'])
			dbquery.inserttodb(sql)

		
		
	sql="SELECT * FROM patient WHERE email = '%s'"%(session['email'])
	datas = dbquery.fetchall(sql)
	sql="SELECT * FROM posts where email = '%s'"%(session['email'])
	posts = dbquery.fetchall(sql)
	return render_template('patient_dash.html',datas=datas,posts=posts)


@app.route('/profile/<string:email>',methods=['GET','POST'])
@is_logged_in						#Can only be accessed if logged in
def profile(email):
	#usr=session['userno']	#Recieving the userid for db manipulation from the initilised session
	#sql="SELECT * FROM PROJECTS WHERE USERID = %s"%(usr)
	#projects=dbquery.fetchall(sql)
	if request.method=='POST':
		title = request.form['title']
		remark = request.form['remark']
		app.config['UPLOAD_FOLDER']="/Users/pranoy/Desktop/medi-fi/static/uploads/%s"%(email)
		if not os.path.exists(app.config['UPLOAD_FOLDER']):
			os.makedirs(app.config['UPLOAD_FOLDER'])
		try:
			f = request.files['file']
			f.save(os.path.join(app.config['UPLOAD_FOLDER'],f.filename))
			
			sql="INSERT INTO posts(email,title,remark,image,post_by) VALUES('%s','%s' ,'%s','%s','%s')"%(email,title,remark,f.filename,session['id'])
			dbquery.inserttodb(sql)
			path = app.config['UPLOAD_FOLDER']+'/'+f.filename
			
			bashCommand = "python3 /Users/pranoy/Desktop/medi-fi/ml/predict.py %s"%(path)
			print(bashCommand)
			import subprocess
			process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
		except:
			sql="INSERT INTO posts(email,title,remark,post_by) VALUES('%s','%s' ,'%s','%s')"%(email,title,remark,session['id'])
			dbquery.inserttodb(sql)

		
		
	sql="SELECT * FROM patient WHERE email = '%s'"%(email)
	datas = dbquery.fetchall(sql)
	sql="SELECT * FROM posts where email = '%s'"%(email)
	posts = dbquery.fetchall(sql)
	return render_template('profile.html',datas=datas,posts=posts)

#========================== Tools =============================
@app.route('/register_patient',methods=['GET','POST'])
@is_logged_in						#Can only be accessed if logged in
def register_patient():
	if request.method== 'POST':
		name = request.form['name']
		age = request.form['age']
		blood = request.form['bloodgroup']
		weight = request.form['weight']
		height = request.form['height']
		email = request.form['email']
		gender = request.form['gender']
		phno = request.form['phno']
		issue = request.form['issue']
		
		sql="INSERT INTO patient(nurseid,name,age,blood,weight,height,email,phno,gender,issue) VALUES('%s','%s' ,'%s','%s','%s','%s' ,'%s','%s','%s','%s')"%(session['id'],name,age,blood,weight,height,email,phno,gender,issue)
		dbquery.inserttodb(sql)	#connecting to db model

		message="Patient Registration Successful"
		return render_template('register_patient.html',message=message)
	return render_template('register_patient.html')


@app.route('/medicine_data',methods=['GET','POST'])
@is_logged_in						#Can only be accessed if logged in
def medicine_data():
	if request.method== 'POST':
		name = request.form['medicinename']
		disease = request.form['disease']
		cost = request.form['cost']
		
		sql="INSERT INTO medicine(userid,medicine,disease,cost) VALUES('%s','%s' ,'%s','%s')"%(session['id'],name,disease,cost)
		dbquery.inserttodb(sql)	#connecting to db model
		message="Medicine Added to Database"
		return render_template('medicine_data.html',message=message)
	return render_template('medicine_data.html')

@app.route('/auth',methods=['GET','POST'])						#Can only be accessed if logged in
def auth():
	if request.method == 'POST':
		nurse = request.form['nurse']
		patient = request.form['patient']
		print(nurse,patient)
		sql = "INSERT INTO rfid(nurse,patient) VALUES('%s','%s')"%(nurse,patient)
		dbquery.inserttodb(sql)
		return "200"
	#usr=session['userno']	#Recieving the userid for db manipulation from the initilised session
	sql="SELECT * FROM rfid "
	info=dbquery.fetchall(sql)
	return render_template('nurse_dash.html',info=info)

@app.route('/appointment_doctor',methods=['GET','POST'])
@is_logged_in						#Can only be accessed if logged in
def appointment_doctor():
	if request.method== 'POST':
		patient = request.form['patient']
		doctor = request.form['doctor']
		date = request.form['date']
		sql = "SELECT * from patient where name = '%s'"%(patient)
		data  = dbquery.fetchall(sql)
		patientEmail = data[0][5]
		sql = "SELECT * from users where name = '%s' and type = 'Doctor'"%(doctor)
		data = dbquery.fetchall(sql)
		doctorEmail = data[0][2]
		sql = "SELECT * from users where userno = '%s' "%(session['id'])
		data = dbquery.fetchall(sql)
		nurse = data[0][1]

		sql="INSERT INTO appointment(userid,patient,doctor,date,patientEmail,doctorEmail,nurseemail,nurse) VALUES('%s','%s' ,'%s','%s','%s','%s','%s','%s')"%(session['id'],patient,doctor,date,patientEmail,doctorEmail,session['email'],nurse)
		dbquery.inserttodb(sql)	#connecting to db model
		message="Appointment Created"
		return render_template('appointment.html',message=message)
	sql = "select name from patient "
	patients=dbquery.fetchall(sql)
	sql = "select name from users where type ='Doctor'"
	doctors = dbquery.fetchall(sql)
	return render_template('appointment.html',patients=patients,doctors=doctors)

@app.route('/appointment_patient',methods=['GET','POST'])
@is_logged_in						#Can only be accessed if logged in
def appointment_patient():
	if request.method== 'POST':
		
		doctor = request.form['doctor']
		date = request.form['date']
		sql = "SELECT * from patient where email = '%s'"%(session['email'])
		data  = dbquery.fetchall(sql)
		patientEmail = session['email']
		patient = data[0][0]
		sql = "SELECT * from users where name = '%s' and type = 'Doctor'"%(doctor)
		data = dbquery.fetchall(sql)
		doctorEmail = data[0][2]
		sql = "SELECT * from users where userno = '%s' "%(session['id'])
		data = dbquery.fetchall(sql)
		nurse = data[0][1]

		sql="INSERT INTO appointment(userid,patient,doctor,date,patientEmail,doctorEmail,nurseemail,nurse) VALUES('%s','%s' ,'%s','%s','%s','%s','%s','%s')"%(session['id'],patient,doctor,date,patientEmail,doctorEmail,session['email'],nurse)
		dbquery.inserttodb(sql)	#connecting to db model
		message="Appointment Created"
		return render_template('appointment_patient.html',message=message)
	
	sql = "select name from users where type ='Doctor'"
	doctors = dbquery.fetchall(sql)
	return render_template('appointment_patient.html',doctors=doctors)

@app.route('/appointment',methods=['GET','POST'])
@is_logged_in						#Can only be accessed if logged in
def appointment():
	if request.method== 'POST':
		patient = request.form['patient']
		doctor = request.form['doctor']
		date = request.form['date']
		sql = "SELECT * from patient where name = '%s'"%(patient)
		data  = dbquery.fetchall(sql)
		patientEmail = data[0][5]
		sql = "SELECT * from users where name = '%s' and type = 'Doctor'"%(doctor)
		data = dbquery.fetchall(sql)
		doctorEmail = data[0][2]
		sql = "SELECT * from users where userno = '%s' and type = 'Nurse'"%(session['id'])
		data = dbquery.fetchall(sql)
		nurse = data[0][1]

		sql="INSERT INTO appointment(userid,patient,doctor,date,patientEmail,doctorEmail,nurseemail,nurse) VALUES('%s','%s' ,'%s','%s','%s','%s','%s','%s')"%(session['id'],patient,doctor,date,patientEmail,doctorEmail,session['email'],nurse)
		dbquery.inserttodb(sql)	#connecting to db model
		message="Appointment Created"
		return render_template('appointment.html',message=message)
	sql = "select name from patient where nurseid ='%s'"%(session['id'])
	patients=dbquery.fetchall(sql)
	sql = "select name from users where type ='Doctor'"
	doctors = dbquery.fetchall(sql)
	return render_template('appointment.html',patients=patients,doctors=doctors)

@app.route('/allotment',methods=['GET','POST'])
@is_logged_in						#Can only be accessed if logged in
def allotment():
	email=session['email']	#Recieving the userid for db manipulation from the initilised session
	sql = "Select * from appointment where doctoremail = '%s'"%(email)
	appointments=dbquery.fetchall(sql)
	return render_template('allotment.html',appointments=appointments)
	

@app.route('/', methods=['GET','POST'])
def index():
	return render_template('index.html')

if __name__=='__main__':
	app.secret_key='secret123' #for flash messaging
	app.run(threaded=True,host="0.0.0.0",port=80,debug=True) #Debugger is set to 1 for testing and overriding the default port to http port
