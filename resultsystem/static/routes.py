from crypt import methods
from flask import render_template, url_for, flash, redirect,request, session
from resultsystem import app
from resultsystem.forms import AdminLoginForm
from resultsystem.models import Student
from resultsystem import db
import os
import smtplib
from email.message import EmailMessage
import random
import imghdr #Image type
import pdfkit
from PyPDF2 import PdfFileWriter, PdfFileReader

posts = [

     {
        'author':'Fynd Academy',
        'title':'Welcome to Fynd Results',
        'content':'Result system model to display Fynd Academy grads result ',
        'date_posted':'April 21,2018'
    }

]

@app.route("/", methods=['GET','POST'])
def home():
    if request.method == 'POST':
        rollno = request.form['rollno']
        name = request.form['name']
        data = Student.query.get(rollno)
        if data is None:
            flash("Please Enter Valid Roll NO", "info")
            return redirect('/')
        dbname = data.name
        if name == dbname:
            emaildb = data.email
            session['email'] = (emaildb,rollno) #will store this in session for resend otp

            # x = generateOtp()
            # sendOtp(emaildb,x)   
            return render_template("validateotp.html",rollno = rollno)
        else:
            flash("Roll No associated with name not found in DB", "info")
            return redirect('/')
    return render_template("home.html")


@app.route("/about")
def about():
    return render_template('about.html', title="About")

@app.route("/adminlogin", methods=['GET', 'POST'])
def login():
    form = AdminLoginForm()
    if request.method == "POST":
        
        if form.validate_on_submit():
            if form.username.data == 'adminblog' and form.password.data == 'password':
                session['logged_in'] = True
                flash('Yoe have been logged in!', 'success')
                return redirect("/adminview")
            else:
                flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('adminlogin.html', title="Login", form=form)


@app.route("/adminview",methods=['GET','POST'])
def add():
    if 'logged_in' in session:
            
        if request.method == 'POST':
            rollno = request.form.get('rollno')
            name = request.form.get('name')
            email = request.form.get('email')
            mobile = request.form.get('mobile')
            math_marks = request.form.get('math_marks')
            science_marks = request.form.get('science_marks')
            english_marks = request.form.get('english_marks')

            stu= Student(rollno=rollno, name=name, email=email, mobile=mobile, math_marks=math_marks, science_marks=science_marks, english_marks=english_marks)
            #This will Work to handle Exception IF again Same data is tried to added
            rollnodb = Student.query.get(rollno)
            if rollnodb is not None:
                flash("Roll No already Exist", "info")
                return redirect("/adminview")

            #Else if No Exception Then Add the data
            db.session.add(stu)
            db.session.commit()

        alldata = Student.query.all()
        return render_template("adminview.html",alldata=alldata)
    return redirect(url_for('adminlogin'))

@app.route('/insert', methods = ['POST'])
def insert():

    if request.method == "POST":
        flash("Data Inserted Successfully")
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        #cur = mysql.connection.cursor()
        #cur.execute("INSERT INTO students (name, email, phone) VALUES (%s, %s, %s)", (name, email, phone))
        #mysql.connection.commit()
        return redirect(url_for('Index'))



@app.route("/validateotp/<int:rollno>", methods=['POST'])
def validateotp(rollno):
    if request.method == 'POST':

        data = Student.query.get(rollno)
        emaildb = data.email 
        # mathmark=data.math_marks
        # engmark=data.english_marks

        html = render_template('resultdata.html',data=data)

        userotp = request.form['otp']

        if 'response' in session: #Checking for response in session
            s = session['response']
            session.pop('response',None)
            if s == str(userotp):

                # if  otp == int(userotp):
                msg = EmailMessage()
                msg['Subject'] = 'Mail from akash server'
                msg['From'] = 'resultservertest@gmail.com'
                msg['To'] = emaildb
                # msg.set_content("Your Password is last 4 digit of mobile no")
                html_msg = html
                
                msg.add_alternative(html_msg, subtype='html')
                
                # adding the Image Attachment
                with open('app/static/fynd.jpeg','rb') as attach_file:
                    image_name = attach_file.name
                    image_type = imghdr.what(attach_file.name)
                    image_data = attach_file.read()

                msg.add_attachment(image_data, maintype='image',subtype=image_type,filename=image_name)
                
                #mobile value taken from db to use it in password of pdf
                # mobile = data.mobile
                # encrypt_pdf(html,mobile) #call the function to generate and encrypt PDF

                                
                # adding the PDF Attachment
                # with open("StudentData_Encrypted.pdf", 'rb') as fp:
                #     pdf_data = fp.read()
                #     ctype = 'application/octet-stream'
                #     maintype, subtype = ctype.split('/', 1)
                #     msg.add_attachment(pdf_data, maintype=maintype, subtype=subtype, filename='StudentData.pdf')
                    

                with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                    smtp.login('resultservertest@gmail.com', os.environ.get('PASS'))
                        
                    smtp.send_message(msg)

                # return render_template("endpage.html",message="Check your mail for the result")
                return redirect("/endpage")
            return render_template("home.html", msg = "Otp not verified Wrong OTP!")
        return render_template("home.html", msg = "Session Expired (Otp Already Used) Try again !")