from django.contrib import messages
from django.shortcuts import redirect, render
from .models import *

def guestindex(request):
    return render(request, 'Guest/index.html')

def about_us(request):
    return render(request, 'Guest/about.html')

def antenatalcare(request):
    return render(request, 'Guest/antenatalcare.html')

def ultrasound(request):
    return render(request, 'Guest/ultrasound.html')

def consultation(request):
    return render(request, 'Guest/consultation.html')

def trimestermonitor(request):
    return render(request, 'Guest/trimestermonitor.html')

def nutritioncare(request):
    return render(request, 'Guest/nutritioncare.html')

def safedelivery(request):
    return render(request, 'Guest/safedelivery.html')

def contact(request):
    return render(request, 'Guest/contact.html')

def login(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "").strip()

        try:
            # Try case-insensitive lookup for email/username
            user = tbl_login.objects.get(
                user_name__iexact=username,
                password=password
            )

            # check status (case-insensitive)
            if user.status.lower() != "active":
                messages.error(request, f"Your account status is '{user.status}'. Please contact support.")
                return render(request, "Guest/login.html")

            # Check Doctor/Patient specific status
            from adminapp.models import tbl_doctor, tbl_patient
            
            doctor_obj = None
            patient_obj = None
            
            if user.role == "Doctor":
                try:
                    doctor_obj = tbl_doctor.objects.get(login_id=user)
                    if doctor_obj.status != "active":
                        messages.error(request, "Your doctor account is currently inactive. Please contact the administrator.")
                        return render(request, "Guest/login.html")
                except tbl_doctor.DoesNotExist:
                    messages.error(request, "Doctor profile not found. Please contact support.")
                    return render(request, "Guest/login.html")
            
            elif user.role == "Patient":
                try:
                    patient_obj = tbl_patient.objects.get(login_id=user)
                    if patient_obj.status in ["Delivered", "Miscarriage", "Transferred"]:
                        messages.error(request, f"Your account status is '{patient_obj.status}'. Please contact support for assistance.")
                        return render(request, "Guest/login.html")
                except tbl_patient.DoesNotExist:
                    messages.error(request, "Patient profile not found. Please contact support.")
                    return render(request, "Guest/login.html")

            # store session
            request.session['login_id'] = user.login_id
            request.session['role'] = user.role

            # Send login alert email for security
            from adminapp.utils import send_email
            if user.role == "Patient" and patient_obj:
                try:
                    subject = "Login Alert - Bloom Moms Care"
                    message = f"""Dear {patient_obj.patient_name},

You have successfully logged into your Bloom Moms Care account.

If this wasn't you, please contact support immediately.

Regards,
Bloom Moms Care Team"""
                    result = send_email(subject, message, patient_obj.email)
                    print(f"✓ Login email sent to {patient_obj.email}: {result}")
                except Exception as e:
                    print(f"✗ Login email error (Patient): {str(e)}")
            elif user.role == "Doctor" and doctor_obj:
                try:
                    subject = "Login Alert - Bloom Moms Care"
                    message = f"""Dear Dr. {doctor_obj.doctor_name},

You have successfully logged into your Bloom Moms Care account.

If this wasn't you, please contact support immediately.

Regards,
Bloom Moms Care Team"""
                    result = send_email(subject, message, doctor_obj.email)
                    print(f"✓ Login email sent to {doctor_obj.email}: {result}")
                except Exception as e:
                    print(f"✗ Login email error (Doctor): {str(e)}")

            # role-based redirect
            if user.role == "Admin":
                messages.success(request, f"Welcome back, Admin!")
                return redirect("adminapp:adminindex")
            elif user.role == "Doctor":
                messages.success(request, f"Welcome back, Doctor!")
                return redirect("doctorapp:doctorindex")
            elif user.role == "Patient":
                messages.success(request, f"Welcome back!")
                return redirect("patientapp:patientindex")
            else:
                messages.error(request, "Invalid role")

        except tbl_login.DoesNotExist:
            # Add detailed error logging for debugging
            print(f"Login failed - Username: '{username}', Password: '{password}'")
            
            # Check if username exists but password is wrong or status is inactive
            if tbl_login.objects.filter(user_name__iexact=username).exists():
                user_found = tbl_login.objects.get(user_name__iexact=username)
                print(f"User found with username '{username}' - Status: '{user_found.status}', Role: {user_found.role}")
                
                if user_found.password != password:
                    messages.error(request, "Invalid password. Please try again.")
                elif user_found.status.lower() != "active":
                    messages.error(request, f"Your account status is '{user_found.status}'. Please contact support.")
                else:
                    messages.error(request, "Unable to login. Please contact support.")
            else:
                print(f"No user found with username '{username}'")
                messages.error(request, "Invalid username or password. Please try again.")

    return render(request, "Guest/login.html")
