import os
from django.core.files.storage import FileSystemStorage
import pymysql
import datetime
import pyqrcode
import png
from pyqrcode import QRCode
from django.shortcuts import render
from django.template import RequestContext
from django.contrib import messages
from django.http import HttpResponse
from PIL import Image
import face_recognition
import time
import cv2
import numpy as np
import base64
import random
import smtplib
from datetime import date

global names, encodings, username, std_name, email_id
face_detection = cv2.CascadeClassifier('model/haarcascade_frontalface_default.xml')

def loadModel():
    global names, encodings
    if os.path.exists("model/encoding.npy"):
        encodings = np.load("model/encoding.npy")
        names = np.load("model/names.npy")        
    else:
        encodings = []
        names = []
loadModel()

def AddFacultyAction(request):
    if request.method == 'POST':
        fname = request.POST.get('t1', False)
        qualification = request.POST.get('t2', False)
        teaching = request.POST.get('t3', False)
        phone = request.POST.get('t4', False)
        email = request.POST.get('t5', False)
        address = request.POST.get('t6', False)
        user = request.POST.get('t7', False)
        password = request.POST.get('t8', False)
        output = "none"
        con = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'std_attendance1',charset='utf8')
        with con:
            cur = con.cursor()
            cur.execute("select username FROM faculty")
            rows = cur.fetchall()
            for row in rows:
                if row[0] == user:
                    output = user+" username already exists"
                    break
        if output == 'none':
            db_connection = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'std_attendance1',charset='utf8')
            db_cursor = db_connection.cursor()
            student_sql_query = "INSERT INTO faculty VALUES('"+fname+"','"+qualification+"','"+teaching+"','"+phone+"','"+email+"','"+address+"','"+user+"','"+password+"')"
            db_cursor.execute(student_sql_query)
            db_connection.commit()
            output = "New faculty details successfully added"
            context= {'data':output}
            return render(request, 'AddFaculty.html', context)
        else:
            context= {'data':output}
            return render(request, 'AddFaculty.html', context)

def ViewStudentAttendanceAction(request):
    if request.method == 'POST':
        global username
        from_date = request.POST.get('t2', False)
        to_date = request.POST.get('t3', False)
        from_dd = str(datetime.datetime.strptime(from_date, "%d-%b-%Y").strftime("'%Y-%m-%d'"))
        to_dd = str(datetime.datetime.strptime(to_date, "%d-%b-%Y").strftime("'%Y-%m-%d'"))
        columns = ['Student ID', 'Presence Date','']
        output = '<table border=1 align=center width=100%>'
        font = '<font size="" color="black">'
        output += "<tr>"
        for i in range(len(columns)):
            output += "<th>"+font+columns[i]+"</th>"            
        output += "</tr>"
        con = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'std_attendance1',charset='utf8')
        with con:
            cur = con.cursor()
            cur.execute("select * from mark_attendance where studentID='"+username+"' and attended_date between "+from_dd+" and "+to_dd)
            rows = cur.fetchall()
            for row in rows:
                output += "<tr>"
                output += "<td>"+font+str(row[0])+"</td>"
                output += "<td>"+font+str(row[1])+"</td></tr>"
        context= {'data': output+"</table><br/><br/><br/><br/>"}
        return render(request, 'StudentScreen.html', context)

def ViewStudentAttendance(request):
    if request.method == 'GET':
        return render(request, 'ViewStudentAttendance.html', {})

def ViewAttendanceAction(request):
    
    if request.method == 'POST':
        from_date = request.POST.get('t2', False)
        to_date = request.POST.get('t3', False)

        course = request.POST.get('course', False)
        year = request.POST.get('year', False)
        semester = request.POST.get('semester', False)



        # Parse to datetime objects (for calculation)
        from_date_obj = datetime.datetime.strptime(from_date, "%d-%b-%Y")
        to_date_obj = datetime.datetime.strptime(to_date, "%d-%b-%Y")

        # Format for SQL queries
        from_dd = from_date_obj.strftime("%Y-%m-%d")
        to_dd = to_date_obj.strftime("%Y-%m-%d")

        # Calculate total days (inclusive)
        total_days = (to_date_obj - from_date_obj).days + 1       

        columns = ['Student ID', 'Days Present', 'Total Working Days', 'Attendance %']
        output = '<table border=1 align=center width=60%>'
        font = '<font size="" color="black">'
        output += "<tr>"
        for col in columns:
            output += "<th>" + font + col + "</th>"
        output += "</tr>"

        con = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='root',
                              database='std_attendance1', charset='utf8')
        with con:
            cur = con.cursor()

           

            # Get students of selected batch using parameterized query
            cur.execute("""
                SELECT studentID FROM addstudent 
                WHERE course_name=%s AND course_year=%s AND semester=%s
            """, (course, year, semester))
            students = cur.fetchall()

            for student in students:
                sid = student[0]
                # Count present days using parameterized query
                cur.execute("""
                    SELECT COUNT(*) FROM mark_attendance 
                    WHERE studentID=%s AND attended_date BETWEEN %s AND %s
                """, (sid, from_dd, to_dd))
                present_days = cur.fetchone()[0]

                # Avoid division by zero
                if total_days > 0:
                    percentage = round((present_days / total_days) * 100, 2)
                else:
                    percentage = 0

                output += "<tr>"
                output += f"<td>{font}{sid}</td>"
                output += f"<td>{font}{present_days}</td>"
                output += f"<td>{font}{total_days}</td>"
                output += f"<td>{font}{percentage}%</td>"
                output += "</tr>"

        context = {'data': output + "</table><br/><br/><br/><br/>"}
        return render(request, 'FacultyScreen.html', context)

def ViewAttendance(request):
    
    if request.method == 'GET':
        font = '<font size="" color="black">'
        output = ''

        # Course dropdown
        output += '<tr><td>' + font + 'Course</td><td><select name="course">'
        course_list = ['Bca', 'Bsc', 'B.tech', 'M.tech', 'Msc', 'Mca', 'Mba']
        for course in course_list:
            output += f'<option value="{course}">{course}</option>'
        output += '</select></td></tr>'

        # Year dropdown
        output += '<tr><td>' + font + 'Year</td><td><select name="year">'
        year_list = ['I', 'II', 'III', 'IV']
        for year in year_list:
            output += f'<option value="{year}">{year}</option>'
        output += '</select></td></tr>'

        # Semester dropdown
        output += '<tr><td>' + font + ' Semester</td><td><select name="semester">'
        sem_list = ['I', 'II']
        for sem in sem_list:
            output += f'<option value="{sem}">{sem}</option>'
        output += '</select></td></tr>'

        context = {'data1': output}
        return render(request, 'ViewAttendance.html', context)


def ViewAdminAttendanceAction(request):
    if request.method == 'POST':
        from_date = request.POST.get('t2', False)
        to_date = request.POST.get('t3', False)

        course = request.POST.get('course', False)
        year = request.POST.get('year', False)
        semester = request.POST.get('semester', False)



        # Parse to datetime objects (for calculation)
        from_date_obj = datetime.datetime.strptime(from_date, "%d-%b-%Y")
        to_date_obj = datetime.datetime.strptime(to_date, "%d-%b-%Y")

        # Format for SQL queries
        from_dd = from_date_obj.strftime("%Y-%m-%d")
        to_dd = to_date_obj.strftime("%Y-%m-%d")

        # Calculate total days (inclusive)
        total_days = (to_date_obj - from_date_obj).days + 1       

        columns = ['Student ID', 'Days Present', 'Total Working Days', 'Attendance %']
        output = '<table border=1 align=center width=60%>'
        font = '<font size="" color="black">'
        output += "<tr>"
        for col in columns:
            output += "<th>" + font + col + "</th>"
        output += "</tr>"

        con = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='root',
                              database='std_attendance1', charset='utf8')
        with con:
            cur = con.cursor()

           

            # Get students of selected batch using parameterized query
            cur.execute("""
                SELECT studentID FROM addstudent 
                WHERE course_name=%s AND course_year=%s AND semester=%s
            """, (course, year, semester))
            students = cur.fetchall()

            for student in students:
                sid = student[0]
                # Count present days using parameterized query
                cur.execute("""
                    SELECT COUNT(*) FROM mark_attendance 
                    WHERE studentID=%s AND attended_date BETWEEN %s AND %s
                """, (sid, from_dd, to_dd))
                present_days = cur.fetchone()[0]

                # Avoid division by zero
                if total_days > 0:
                    percentage = round((present_days / total_days) * 100, 2)
                else:
                    percentage = 0

                output += "<tr>"
                output += f"<td>{font}{sid}</td>"
                output += f"<td>{font}{present_days}</td>"
                output += f"<td>{font}{total_days}</td>"
                output += f"<td>{font}{percentage}%</td>"
                output += "</tr>"

        context = {'data': output + "</table><br/><br/><br/><br/>"}
        return render(request, 'AdminScreen.html', context)



def ViewAdminAttendance(request):
    if request.method == 'GET':
        font = '<font size="" color="black">'
        output = ''

        # Course dropdown
        output += '<tr><td>' + font + 'Course</td><td><select name="course">'
        course_list = ['Bca', 'Bsc', 'B.tech', 'M.tech', 'Msc', 'Mca', 'Mba']
        for course in course_list:
            output += f'<option value="{course}">{course}</option>'
        output += '</select></td></tr>'

        # Year dropdown
        output += '<tr><td>' + font + 'Year</td><td><select name="year">'
        year_list = ['I', 'II', 'III', 'IV']
        for year in year_list:
            output += f'<option value="{year}">{year}</option>'
        output += '</select></td></tr>'

        # Semester dropdown
        output += '<tr><td>' + font + ' Semester</td><td><select name="semester">'
        sem_list = ['I', 'II']
        for sem in sem_list:
            output += f'<option value="{sem}">{sem}</option>'
        output += '</select></td></tr>'

        context = {'data1': output}
        return render(request, 'ViewAdminAttendance.html', context)


def FacultyLoginAction(request):
    if request.method == 'POST':
        global username
        username = request.POST.get('t1', False)
        password = request.POST.get('t2', False)
        index = 0
        emp_name = None
        con = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'std_attendance1',charset='utf8')
        with con:
            cur = con.cursor()
            cur.execute("select username, password FROM faculty")
            rows = cur.fetchall()
            for row in rows:
                if row[0] == username and row[1] == password:
                    index = 1
                    break		
        if index == 1:
            context= {'data':'<font size="3" color="blue">Welcoe '+username+'</font>'}
            return render(request, 'FacultyScreen.html', context)
        else:
            context= {'data':'login failed. Please retry'}
            return render(request, 'FacultyLogin.html', context)

def AdminLoginAction(request):
    global username
    if request.method == 'POST':
        username = request.POST.get('t1', False)
        password = request.POST.get('t2', False)
        if username == 'admin' and password == 'admin':
            context= {'data':'Hello! Administrator'}
            return render(request, 'AdminScreen.html', context)
        else:
            context= {'data':'login failed. Please retry'}
            return render(request, 'AdminLogin.html', context)  

def FacultyLogin(request):
    if request.method == 'GET':
       return render(request, 'FacultyLogin.html', {})

def AddFaculty(request):
    if request.method == 'GET':
       return render(request, 'AddFaculty.html', {})      

def AdminLogin(request):
    if request.method == 'GET':
       return render(request, 'AdminLogin.html', {})

def StudentLogin(request):
    if request.method == 'GET':
       return render(request, 'StudentLogin.html', {})  

def index(request):
    if request.method == 'GET':
       return render(request, 'index.html', {})

def AddStudent(request):
    if request.method == 'GET':
       return render(request, 'AddStudent.html', {})

def isFaceAvailable(username):
    flag = False
    global names
    print(names)
    for i in range(len(names)):
        if names[i] == username:
            flag = True
            break
    return flag    

def StudentLoginAction(request):
    if request.method == 'POST':
        global username, std_name
        username = request.POST.get('t1', False)
        password = request.POST.get('t2', False)
        index = 0
        emp_name = None
        con = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'std_attendance1',charset='utf8')
        with con:
            cur = con.cursor()
            cur.execute("select studentID, password, studentName FROM addstudent")
            rows = cur.fetchall()
            for row in rows:
                if row[0] == username and row[1] == password:
                    std_name = row[2]
                    index = 1
                    break		
        if index == 1:
            flag = isFaceAvailable(username)
            if flag == True:
                context= {'data':'<font size="3" color="blue">Please authenticate your face</font>'}
                return render(request, 'ValidateFace.html', context)
            else:
                context= {'data':'<font size="3" color="blue">Please registered your face</font>'}
                return render(request, 'CaptureFace.html', context)
        else:
            context= {'data':'login failed. Please retry'}
            return render(request, 'StudentLogin.html', context)        

def GenerateCode(request):
    if request.method == 'GET':
        global username
        if os.path.exists("AttendanceApp/static/qrcodes/"+username+".png"):
            os.remove("AttendanceApp/static/qrcodes/"+username+".png")
        url = pyqrcode.create(username)
        url.png('AttendanceApp/static/qrcodes/'+username+'.png', scale = 6)    
        infile = open("AttendanceApp/static/qrcodes/"+username+".png", 'rb')
        data = infile.read()
        infile.close()       

        response = HttpResponse(data, content_type='image/png')
        response['Content-Disposition'] = 'attachment; filename=%s' % username+".png"
        return response

def WebCam(request):
    if request.method == 'GET':
        data = str(request)
        formats, imgstr = data.split(';base64,')
        imgstr = imgstr[0:(len(imgstr)-2)]
        data = base64.b64decode(imgstr)
        if os.path.exists("AttendanceApp/static/photo/test.png"):
            os.remove("AttendanceApp/static/photo/test.png")
        with open('AttendanceApp/static/photo/test.png', 'wb') as f:
            f.write(data)
        f.close()
        context= {'data':"done"}
        return HttpResponse("Image saved")            

def AddStudentAction(request):
    if request.method == 'POST':
        std_id = request.POST.get('t1', False)
        name = request.POST.get('t2', False)
        gender = request.POST.get('t3', False)
        phone = request.POST.get('t4', False)
        email = request.POST.get('t5', False)
        address = request.POST.get('t6', False)
        course = request.POST.get('t7', False)
        year = request.POST.get('t8', False)
        semester = request.POST.get('t9',False)
        password = request.POST.get('t9', False)
        output = "none"
        con = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'std_attendance1',charset='utf8')
        with con:
            cur = con.cursor()
            cur.execute("select studentID FROM addstudent")
            rows = cur.fetchall()
            for row in rows:
                if row[0] == std_id:
                    output = std_id+" student id already exists"
                    break
        if output == 'none':
            db_connection = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'std_attendance1',charset='utf8')
            db_cursor = db_connection.cursor()
            student_sql_query = "INSERT INTO addstudent VALUES('"+std_id+"','"+name+"','"+gender+"','"+phone+"','"+email+"','"+address+"','"+course+"','"+year+"','"+semester+"','"+password+"')"
            db_cursor.execute(student_sql_query)
            db_connection.commit()
            output = "New student details successfully added"
            context= {'data':output}
            return render(request, 'AddStudent.html', context)
        else:
            context= {'data':output}
            return render(request, 'AddStudent.html', context)
      
def saveFace():
    global names, encodings
    encodings = np.asarray(encodings)
    names = np.asarray(names)
    np.save("model/encoding", encodings)
    np.save("model/names", names)

def saveUser(request):
    if request.method == 'POST':
        global username, std_name
        global encodings, names
        img = cv2.imread('AttendanceApp/static/photo/test.png')
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        face_component = None
        faces = face_detection.detectMultiScale(gray, 1.3,5)
        page = "CaptureFace.html"
        status = '<font size="3" color="blue">Unable to detect face. Please retry</font>'
        for (x, y, w, h) in faces:
            face_component = img[y:y+h, x:x+w]
        if face_component is not None:
            img = cv2.resize(img, (600, 600))
            if os.path.exists("AttendanceApp/static/photo/test.png"):
                os.remove("AttendanceApp/static/photo/test.png")
            cv2.imwrite("AttendanceApp/static/photo/test.png", img)
            image = face_recognition.load_image_file("AttendanceApp/static/photo/test.png")
            encoding = face_recognition.face_encodings(image)
            print("encoding "+str(encoding))
            if len(encoding) > 0 and username not in names:
                encoding = encoding[0]
                if len(encodings) == 0:
                    encodings.append(encoding)
                    names.append(username)
                else:
                    encodings = encodings.tolist()
                    names = names.tolist()
                    encodings.append(encoding)
                    names.append(username)
                saveFace()
                status = '<font size="3" color="blue">User with Face Details added to Database</font><br/><br/>'
                page = "StudentScreen.html"                          
        context= {'data': status}
        return render(request, page, context)

def isStdExists(code):
    email_id = ""
    connect = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'std_attendance1',charset='utf8')
    with connect:
        curs = connect.cursor()
        curs.execute("select email FROM addstudent where studentID='"+code+"'")
        rows = curs.fetchall()
        for row in rows:
            email_id = row[0]
            break
    return email_id

def isAttendanceTaken(code):
    flag = False
    current_date = str(time.strftime('%Y-%m-%d'))
    connect = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'std_attendance1',charset='utf8')
    with connect:
        curs = connect.cursor()
        curs.execute("select * FROM mark_attendance where studentID='"+code+"' and attended_date='"+current_date+"'")
        rows = curs.fetchall()
        for row in rows:
            flag = True
            break
    return flag

def sendEmail(email, msg):
    em = []
    em.append(email)
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as connection:
        email_address = 'kaleem202120@gmail.com'
        email_password = 'xyljzncebdxcubjq'
        connection.login(email_address, email_password)
        connection.sendmail(from_addr="kaleem202120@gmail.com", to_addrs=em, msg=msg)

def takeAttendance(std_code):
    error = "Internal error occured"
    current_date = str(time.strftime('%Y-%m-%d'))
    attended_date = isAttendanceTaken(std_code)
    email_id = isStdExists(std_code)
    if attended_date == False and len(email_id) > 0:
        connect = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'std_attendance1',charset='utf8')
        curs = connect.cursor()
        curs.execute("INSERT INTO mark_attendance(studentID, attended_date) VALUES('"+std_code+"','"+current_date+"')")
        connect.commit()
        error = "Attendance Accepted for Student ID "+std_code
        sendEmail(email_id, "Your child "+std_code+" Present today "+str(date.today()))
    if attended_date == True:
        error = "Attendance Accepted only one time for current day"    
    return error

def MarkAdminAttendanceAction(request):
    if request.method == 'GET':
        std_code = request.GET['t1']
        msg = takeAttendance(std_code)
        context= {'data':msg}
        return render(request, "AdminScreen.html", context)

def MarkAdminAttendance(request):
    if request.method == 'GET':
        return render(request, 'MarkAdminAttendance.html', {})

def MarkAttendanceAction(request):
    if request.method == 'GET':
        std_code = request.GET['t1']
        msg = takeAttendance(std_code)
        context= {'data':msg}
        return render(request, "FacultyScreen.html", context)

def MarkAttendance(request):
    if request.method == 'GET':
        return render(request, 'MarkAttendance.html', {})    

def ValidateUser(request):
    if request.method == 'POST':
        global username, encodings, names, std_name
        predict = "none"
        page = "ValidateFace.html"
        status = '<font size="3" color="blue">unable to predict user</font>'
        img = cv2.imread('AttendanceApp/static/photo/test.png')
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        face_component = None
        faces = face_detection.detectMultiScale(img,scaleFactor=1.1,minNeighbors=5,minSize=(30,30),flags=cv2.CASCADE_SCALE_IMAGE)
        status = '<font size="3" color="blue">Unable to predict.Please retry</font>'
        if len(faces) > 0:
            faces = sorted(faces, reverse=True,key=lambda x: (x[2] - x[0]) * (x[3] - x[1]))[0]
            (fX, fY, fW, fH) = faces
            face_component = gray[fY:fY + fH, fX:fX + fW]
            if face_component is not None:
                img = cv2.resize(img, (600, 600))
                rgb_small_frame = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # Convert the frame to RGB color space
                face_locations = face_recognition.face_locations(rgb_small_frame)  # Locate faces in the frame
                face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)  # Encode faces in the frame
                for face_encoding in face_encodings:
                    matches = face_recognition.compare_faces(encodings, face_encoding)  # Compare face encodings
                    face_distance = face_recognition.face_distance(encodings, face_encoding)  # Calculate face distance
                    best_match_index = np.argmin(face_distance)  # Get the index of the best match
                    print(best_match_index)
                    if matches[best_match_index]:  # If the face is a match
                        name = names[best_match_index]  # Get the corresponding name
                        predict = name
                        break
            if predict == username:            
                status = '<font size="4" color="blue">Welcome '+std_name+"</font>"
                page = "StudentScreen.html"
        else:
            status = "unable to detect face"
        context= {'data':status}
        return render(request, page, context)


    
