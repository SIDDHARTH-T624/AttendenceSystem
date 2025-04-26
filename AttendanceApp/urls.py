from django.urls import path

from . import views

urlpatterns = [path("index.html", views.index, name="index"),
			path("StudentLogin.html", views.StudentLogin, name="StudentLogin"),
			path("StudentLoginAction", views.StudentLoginAction, name="StudentLoginAction"),
			path("FacultyLogin.html", views.FacultyLogin, name="FacultyLogin"),
			path("FacultyLoginAction", views.FacultyLoginAction, name="FacultyLoginAction"),
			path("AdminLogin.html", views.AdminLogin, name="AdminLogin"),
			path("AdminLoginAction", views.AdminLoginAction, name="AdminLoginAction"),
			path("AddStudent.html", views.AddStudent, name="AddStudent"),
			path("AddStudentAction", views.AddStudentAction, name="AddStudentAction"),
			path("MarkAdminAttendance", views.MarkAdminAttendance, name="MarkAdminAttendance"),
			path("ViewAdminAttendance", views.ViewAdminAttendance, name="ViewAdminAttendance"),
			path("MarkAdminAttendanceAction", views.MarkAdminAttendanceAction, name="MarkAdminAttendanceAction"),
			path("MarkAttendance", views.MarkAttendance, name="MarkAttendance"),
			path("MarkAttendanceAction", views.MarkAttendanceAction, name="MarkAttendanceAction"),
			path("ViewAttendance", views.ViewAttendance, name="ViewAttendance"),
			path("ViewAttendanceAction", views.ViewAttendanceAction, name="ViewAttendanceAction"),
			path("ViewAdminAttendanceAction", views.ViewAdminAttendanceAction, name="ViewAdminAttendanceAction"),
			path("WebCam", views.WebCam, name="WebCam"),
	                path("saveUser", views.saveUser, name="saveUser"),
			path("ValidateUser", views.ValidateUser, name="ValidateUser"),
			path("GenerateCode", views.GenerateCode, name="GenerateCode"),
			
			path("ViewStudentAttendance", views.ViewStudentAttendance, name="ViewStudentAttendance"),
			path("ViewStudentAttendanceAction", views.ViewStudentAttendanceAction, name="ViewStudentAttendanceAction"),

			path("AddFaculty.html", views.AddFaculty, name="AddFaculty"),
			path("AddFacultyAction", views.AddFacultyAction, name="AddFacultyAction"),
]
