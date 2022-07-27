import subprocess
import sys
from flask import Blueprint, render_template,flash, redirect,request, session
from app.forms import AdminLoginForm
from app.constants import Email_data
from app.constants import Admin_data
from app.models import Student
from .extenstion import db
import os
import smtplib
from email.message import EmailMessage
import random

import pdfkit
from PyPDF2 import PdfFileWriter, PdfFileReader

main = Blueprint('main', __name__)

app = main

def generateOtp():
    return random.randint(1111,9999)

def sendOtp(email,x):
        msg = EmailMessage()
        msg['Subject'] = 'OTP FROM Fynd Academy'
        msg['From'] = Email_data.EMAIL
        msg['To'] = email
        # x = generateOtp()
        msg.set_content(str(x))
        session['response'] = str(x)  #Storing otp in session

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(Email_data.EMAIL, Email_data.PASSWORD)
                
            smtp.send_message(msg)

            
if 'DYNO' in os.environ:
    print ('loading wkhtmltopdf path on heroku')
    WKHTMLTOPDF_CMD = subprocess.Popen(
        ['which', os.environ.get('WKHTMLTOPDF_BINARY', 'wkhtmltopdf-pack')], # Note we default to 'wkhtmltopdf' as the binary name
        stdout=subprocess.PIPE).communicate()[0].strip()
else:
    print ('loading wkhtmltopdf path on localhost')
    MYDIR = os.path.dirname(__file__)    
    WKHTMLTOPDF_CMD = os.path.join(MYDIR + "/static/executables/bin/", "wkhtmltopdf.exe")

def encrypt_pdf(html,mobile):
    # config = pdfkit.configuration(wkhtmltopdf='/bin/wkhtmltopdf')

    # os.environ['PATH'] += os.pathsep + os.path.dirname(sys.executable) 
    # WKHTMLTOPDF_CMD = subprocess.Popen(['which', os.environ.get('WKHTMLTOPDF_BINARY', 'wkhtmltopdf')], 
    # stdout=subprocess.PIPE).communicate()[0].strip()
    # pdfkit_config = pdfkit.configuration(wkhtmltopdf=WKHTMLTOPDF_CMD)


    # WKHTMLTOPDF_CMD = subprocess.Popen(
    # ['which', os.environ.get('WKHTMLTOPDF_BINARY', 'wkhtmltopdf-pack')], # Note we default to 'wkhtmltopdf' as the binary name
    #     stdout=subprocess.PIPE).communicate()[0].strip()

    pdfkit.from_string(html,'StudentData.pdf')
    out = PdfFileWriter()
    file = PdfFileReader("StudentData.pdf")  
    # Get number of pages in original file
    num = file.numPages    
    # Iterate through every page of the original 
    # file and add it to our new file.
    for idx in range(num):        
        # Get the page at index idx
        page = file.getPage(idx)        
        # Add it to the output file
        out.addPage(page)        
    # Create a variable password and store 
    # our password in it.
    password = mobile[6:]    
    # Encrypt the new file with the entered password
    out.encrypt(password)    
    # Open a new file "myfile_encrypted.pdf"
    with open("StudentData_Encrypted.pdf", "wb") as f:        
        # Write our encrypted PDF to this file
        out.write(f)

def removePdf():
        pdfdelete=("StudentData_Encrypted.pdf" , "StudentData.pdf")
        os.remove(pdfdelete[0])
        os.remove(pdfdelete[1])

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
    return render_template("home.html")

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
        
        html = render_template('resultdata.html',data=data)
        userotp = request.form['otp']
        if 'response' in session: #Checking for response in session
            s = session['response']
            session.pop('response',None)
            if s == str(userotp):
                # if otp == int(userotp):
                    msg = EmailMessage()
                    msg['Subject'] = 'Fynd Result System'
                    msg['From'] = Email_data.EMAIL
                    msg['To'] = emaildb
                    msg['body'] = "our Password is last 4 digit of mobile no"
                    msg.set_content("Your Password is last 4 digit of mobile no")
                    html_msg = html
                

                    msg.add_alternative(html_msg, subtype='html')
                    msg.add_attachment('''This PDF file is protected. The password to this file is  last 4 digit of mobile number
                                        Example:
                        Your password is : xxxxxx1234''')
                    mobile = data.mobile
                    encrypt_pdf(html,mobile) 
    
                # adding the PDF Attachment
                    with open("StudentData_Encrypted.pdf", 'rb') as fp:
                        pdf_data = fp.read()
                        ctype = 'application/octet-stream'
                        maintype, subtype = ctype.split('/', 1)
                        msg.add_attachment(pdf_data, maintype=maintype, subtype=subtype, filename='StudentData.pdf')
                    
                    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                        smtp.login(Email_data.EMAIL, Email_data.PASSWORD)
                        
                        smtp.send_message(msg)

                # return render_template("endpage.html",message="Check your mail for the result")
                    return redirect("/endpage")
            flash("Invalid OTP .... Please try again", "danger")
        return render_template("home.html")




@app.route("/endpage", methods=['GET','POST'])
def endpage():
    
    removePdf()
    return render_template("endpage.html")


@app.route("/adminlogin", methods=['GET', 'POST'])
def login():
    form = AdminLoginForm()
    if request.method == "POST":
        if form.validate_on_submit():
            if form.username.data == Admin_data.USERNAME  and form.password.data == Admin_data.PASSWORD:
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
        # form = AddStudentForm()
        if request.method == "POST":
            rollno = request.form.get('rollno')
            name = request.form.get('name')
            email = request.form.get('email')
            mobile = request.form.get('mobile')
            math_marks = request.form.get('math_marks')
            science_marks = request.form.get('science_marks')
            english_marks = request.form.get('english_marks')
            stu= Student(rollno=rollno, name=name, email=email, mobile=mobile, math_marks=math_marks, science_marks=science_marks, english_marks=english_marks)        
            if len(mobile)!=10:
                flash("Please enter valid mobile")
                return redirect ('/adminview')
            #This will Work to handle Exception IF again Same data is tried to added
            rollnodb = Student.query.get(rollno)
            if rollnodb is not None:
                flash("Roll No already Exist", "info")
                return redirect ('/adminview')

            alldata = Student.query.all()
            for student in alldata:
                if student.email == email:
                    flash(f"This email already exits: {student.email} ", "info")
                    return redirect ('/adminview')
            
            
                #Else if No Exception Then Add the data
            db.session.add(stu)
            db.session.commit()
            flash("Data Inserted Successfully")
        page = request.args.get('page',1, type=int)
        alldata = Student.query.paginate(page=int(page), per_page=10)
        return render_template("adminview.html", alldata=alldata)
        
    return redirect('/adminlogin')

@app.route("/update/",methods=['POST','GET'])
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
            
            
            if len(stu.mobile)!=10:
                flash("Please enter valid mobile")
                return redirect ('/adminview')
            try:
                db.session.add(stu)
                db.session.commit()
            except Exception:
                db.session.rollback()
                flash(f"This email already exits", "info")
                return redirect ('/adminview')
                

            
            
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





