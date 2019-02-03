import smtplib 
s = smtplib.SMTP('smtp.gmail.com', 587) 
s.starttls() 
s.login("mankaran32@gmail.com", "9872901791") 
message = "yo"
s.sendmail("mankaran32@gmail.com", "rvirmani9@gmail.com", message) 
s.quit() 
