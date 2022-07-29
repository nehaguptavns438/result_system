import pdfkit
import random
from PyPDF2 import PdfFileWriter, PdfFileReader
import os
from email.message import EmailMessage
from app.constants import Email_data
from flask import session
import smtplib



def generateOtp():
    return random.randint(1111,9999)

def encrypt_pdf(html,mobile):
    # pdfkit.from_string(html,'StudentData.pdf', configuration=config)
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