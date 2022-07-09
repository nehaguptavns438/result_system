from crypt import methods
from flask import Blueprint, render_template,flash, redirect,request, session
#from resultsystem import app
from resultsystem.forms import AdminLoginForm
from resultsystem.models import Student
from flask_mail import Mail
from .extenstion import db
import os
import smtplib
from email.message import EmailMessage
import random
import imghdr #Image type
import pdfkit
from PyPDF2 import PdfFileWriter, PdfFileReader

main = Blueprint('main', __name__)

app = main



posts = [

     {
        'author':'Fynd Academy',
        'title':'Welcome to Fynd Results',
        'content':'Result system model to display Fynd Academy grads result ',
        'date_posted':'April 21,2018'
    }

]

def generateOtp():
    return random.randint(1111,9999)

def sendOtp(email,x):
        msg = EmailMessage()
        msg['Subject'] = 'OTP FROM Akash Server'
        msg['From'] = 'examresultsystembot@gmail.com'
        msg['To'] = email
        # x = generateOtp()
        msg.set_content(str(x))
        session['response'] = str(x)  #Storing otp in session

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login('examresultsystembot@gmail.com', 'ksguocbvgsskntcj')
                
            smtp.send_message(msg)

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
        if name.lower() == str(dbname).lower():
            emaildb = data.email
            session['email'] = (emaildb,rollno) #will store this in session for resend otp

            x = generateOtp()
            sendOtp(emaildb,x)   
            return render_template("validateotp.html",rollno = rollno)
        else:
            flash("Roll No associated with name not found in DB", "info")
            return redirect('/')
    return render_template("home.html",posts=posts)

@app.route("/resendotp", methods=['POST'])
def resend():
    if request.method == 'POST':
        
        if 'email' in session: #resend otp
            emaildb = session['email'][0] #resend otp
            x = generateOtp() #resend otp
            sendOtp(emaildb,x) #resend otp
            rollno = session['email'][1]
            return render_template("validateotp.html",rollno = rollno)
        return render_template("home.html")

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
                msg['Subject'] = 'Mail from neha server'
                msg['From'] = 'examresultsystembot@gmail.com'
                msg['To'] = emaildb
                # msg.set_content("Your Password is last 4 digit of mobile no")
                html_msg = html
                
                msg.add_alternative(html_msg, subtype='html')
                
                # adding the Image Attachment
                with open('resultsystem/static/fynd.jpeg','rb') as attach_file:
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
                    smtp.login('examresultsystembot@gmail.com', 'ksguocbvgsskntcj')
                        
                    smtp.send_message(msg)

                # return render_template("endpage.html",message="Check your mail for the result")
                return redirect("/endpage")
            return render_template("home.html", msg = "Otp not verified Wrong OTP!")
        return render_template("home.html", msg = "Session Expired (Otp Already Used) Try again !")

@app.route("/endpage", methods=['GET'])
def endpage():
    #Delete the generated pdf after sending email
    # removePdf()
    return render_template("endpage.html",message="Check your Email for the result")


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

    # ..................ADMIN.......................


@app.route("/adminview",methods=['GET','POST'])
def add():
    if 'logged_in' in session:
        #form = AddStudentForm()
        if request.method == "POST":
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
                return redirect ('/adminview')

                #Else if No Exception Then Add the data
            db.session.add(stu)
            db.session.commit()
            flash("Data Inserted Successfully")
        alldata = Student.query.all()
        
        return render_template("adminview.html", alldata=alldata)
    return redirect('/adminlogin')

@app.route("/update",methods=['POST','GET'])
def update():
    if 'logged_in' in session:

        if request.method == 'POST':
            rollno = request.form.get('rollno')
            name = request.form.get('name')
            email = request.form.get('email')
            mobile = request.form.get('mobile')
            math_marks = request.form.get('math_marks')
            science_marks = request.form.get('science_marks')
            english_marks = request.form.get('english_marks')
            #object of row of the db related to rollno
            stu = Student.query.filter_by(rollno=rollno).first()

            #update new data in db
            stu.rollno = rollno
            stu.name = name
            stu.email = email
            stu.mobile = mobile
            stu.math_marks = math_marks
            stu.science_marks = science_marks
            stu.english_marks = english_marks
            db.session.add(stu)
            db.session.commit()
            flash("Data updated Successfully")
            
            return redirect('/adminview')
            
        return redirect('/adminlogin')

@app.route("/delete/<int:rollno>")
def delete(rollno):
    if 'logged_in' in session:

        stu = Student.query.filter_by(rollno=rollno).first()
        db.session.delete(stu)
        db.session.commit()
        flash("Data Deleted Successfully")
        return redirect("/adminview")
    return redirect('/adminlogin')

@app.route("/logout")
def logout():
    session.pop('logged_in',None)
    return redirect("/adminlogin")





