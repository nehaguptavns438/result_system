from asyncio.log import logger
from flask import Blueprint, render_template, flash, redirect, request, session
from .forms import AdminLoginForm
from .constants import Email_data
from .constants import Admin_data
from .models import Student
from .extenstion import db
import smtplib
from app.utils import encrypt_pdf, generateOtp, sendOtp, removePdf
from email.message import EmailMessage

main = Blueprint("main", __name__)
app = main


@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        rollno = request.form["rollno"]
        name = request.form["name"]
        data = Student.query.get(rollno)
        if data is None:
            flash("Please Enter Valid Roll NO", "info")
            return redirect("/")
        dbname = data.name
        if name.lower() == str(dbname).lower():
            emaildb = data.email
            session["email"] = (
                emaildb,
                rollno,
            )  # will store this in session for resend otp
            # flash('A four digit OTP has been sent to your registered email', 'info')
            x = generateOtp()
            sendOtp(emaildb, x)
            return render_template("validateotp.html", rollno=rollno)
        else:
            flash("Roll No associated with name not found in DB", "info")
            return redirect("/")
    return render_template("home.html")


@app.route("/validateotp/<int:rollno>", methods=["POST"])
def validateotp(rollno):
    if request.method == "POST":
        data = Student.query.get(rollno)
        emaildb = data.email
        html = render_template("resultdata.html", data=data)
        userotp = request.form["otp"]
        if "response" in session:  # Checking for response in session
            s = session["response"]
            session.pop("response", None)
            if s == str(userotp):
                # if otp == int(userotp):
                msg = EmailMessage()
                msg["Subject"] = "Excellent Result System"
                msg["From"] = Email_data.EMAIL
                msg["To"] = emaildb
                msg["body"] = "our Password is last 4 digit of mobile no"
                msg.set_content("Your Password is last 4 digit of mobile no")
                html_msg = html
                msg.add_alternative(html_msg, subtype="html")
                mobile = data.mobile
                try:
                    encrypt_pdf(html, mobile)
                    msg.add_attachment(
                        """This PDF file is protected. The password to this file is  last 4 digit of mobile number
                                        Example:
                        Your password is : xxxxxx1234"""
                    )
                    # adding the PDF Attachment
                    with open("StudentData_Encrypted.pdf", "rb") as fp:
                        pdf_data = fp.read()
                        ctype = "application/octet-stream"
                        maintype, subtype = ctype.split("/", 1)
                        msg.add_attachment(
                            pdf_data,
                            maintype=maintype,
                            subtype=subtype,
                            filename="StudentData.pdf",
                        )
                except Exception as e:
                    logger.exception(f"Can't generate and attach PDF : {e}")

                with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
                    smtp.login(Email_data.EMAIL, Email_data.PASSWORD)
                    smtp.send_message(msg)
                return redirect("/endpage")
            flash("Invalid OTP .... Please try again", "danger")
        return render_template("home.html")


@app.route("/resendotp", methods=["POST"])
def resend():
    if request.method == "POST":
        if "email" in session:  # resend otp
            emaildb = session["email"][0]  # resend otp
            x = generateOtp()  # resend otp
            sendOtp(emaildb, x)  # resend otp
            rollno = session["email"][1]
            return render_template("validateotp.html", rollno=rollno)
        return render_template("home.html")


@app.route("/endpage", methods=["GET", "POST"])
def endpage():
    try:
        removePdf()
    except Exception as e:
        logger.exception(f"PDF not found in root directory : {e}")
    return render_template("endpage.html")


#....................ADMIN.......................


@app.route("/adminlogin", methods=["GET", "POST"])
def login():
    form = AdminLoginForm()
    if request.method == "POST":
        if form.validate_on_submit():
            if (
                form.username.data == Admin_data.USERNAME
                and form.password.data == Admin_data.PASSWORD
            ):
                session["logged_in"] = True
                flash("Yoe have been logged in!", "success")
                return redirect("/adminview")
            else:
                flash(
                    "Login Unsuccessful. Please check username and password", "danger"
                )
    return render_template("adminlogin.html", title="Login", form=form)


@app.route("/adminview", methods=["GET", "POST"])
def add():
    if "logged_in" in session:
        if request.method == "POST":
            rollno = request.form.get("rollno")
            name = request.form.get("name")
            email = request.form.get("email")
            mobile = request.form.get("mobile")
            math_marks = request.form.get("math_marks")
            science_marks = request.form.get("science_marks")
            english_marks = request.form.get("english_marks")
            stu = Student(
                rollno=rollno,
                name=name,
                email=email,
                mobile=mobile,
                math_marks=math_marks,
                science_marks=science_marks,
                english_marks=english_marks,
            )
            if len(mobile) != 10:
                flash("Please enter valid mobile")
                return redirect("/adminview")
            # This will Work to handle Exception IF again Same data is tried to added
            rollnodb = Student.query.get(rollno)
            if rollnodb is not None:
                flash("Roll No already Exist", "info")
                return redirect("/adminview")

            alldata = Student.query.all()
            for student in alldata:
                if student.email == email:
                    flash(f"This email already exits: {student.email} ", "info")
                    return redirect("/adminview")
                # Else if No Exception Then Add the data
            db.session.add(stu)
            db.session.commit()
            flash("Data Inserted Successfully")
        page = request.args.get("page", 1, type=int)
        alldata = Student.query.paginate(page=int(page), per_page=5)
        return render_template("adminview.html", alldata=alldata)
    return redirect("/adminlogin")


@app.route("/update/", methods=["POST", "GET"])
def update():
    if "logged_in" in session:
        if request.method == "POST":
            rollno = request.form.get("rollno")
            name = request.form.get("name")
            email = request.form.get("email")
            mobile = request.form.get("mobile")
            math_marks = request.form.get("math_marks")
            science_marks = request.form.get("science_marks")
            english_marks = request.form.get("english_marks")
            # object of row of the db related to rollno
            stu = Student.query.filter_by(rollno=rollno).first()
            # update new data in db
            stu.rollno = rollno
            stu.name = name
            stu.email = email
            stu.mobile = mobile
            stu.math_marks = math_marks
            stu.science_marks = science_marks
            stu.english_marks = english_marks
            if len(stu.mobile) != 10:
                flash("Please enter valid mobile")
                return redirect("/adminview")
            try:
                db.session.add(stu)
                db.session.commit()
            except Exception:
                db.session.rollback()
                flash(f"This email/mobile already exits in database", "info")
                return redirect("/adminview")
            flash("Data updated Successfully")
            return redirect("/adminview")
        return redirect("/adminlogin")


@app.route("/delete/<int:rollno>")
def delete(rollno):
    if "logged_in" in session:
        stu = Student.query.filter_by(rollno=rollno).first()
        db.session.delete(stu)
        db.session.commit()
        flash("Data Deleted Successfully")
        return redirect("/adminview")
    return redirect("/adminlogin")


@app.route("/logout")
def logout():
    session.pop("logged_in", None)
    return redirect("/adminlogin")
