from django.contrib import messages
from django.shortcuts import redirect, render
from .models import *
from datetime import datetime, timedelta
import random


def _clear_forgot_password_session(request):
    keys = [
        'forgot_password_login_id',
        'forgot_password_otp',
        'forgot_password_expires_at',
    ]
    for key in keys:
        request.session.pop(key, None)


def _get_user_email_for_reset(user):
    """Return the registered email for the given login user based on role."""
    from adminapp.models import tbl_doctor, tbl_patient

    if user.role == 'Patient':
        patient = tbl_patient.objects.filter(login_id=user).first()
        return (patient.email or '').strip().lower() if patient else ''

    if user.role == 'Doctor':
        doctor = tbl_doctor.objects.filter(login_id=user).first()
        return (doctor.email or '').strip().lower() if doctor else ''

    # Fallback for Admin and any other roles.
    return (user.user_name or '').strip().lower()

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
                    if patient_obj.status == "Transferred":
                        messages.error(request, "Your account has been transferred to another facility. Please contact support for assistance.")
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
                return redirect("adminapp:adminindex")
            elif user.role == "Doctor":
                return redirect("doctorapp:doctorindex")
            elif user.role == "Patient":
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


def forgot_password(request):
    if request.method == 'POST':
        recovery_email = request.POST.get('recovery_email', '').strip().lower()

        if not recovery_email:
            messages.error(request, 'Registered email is required.')
            return render(request, 'Guest/forgot_password.html')

        # Primary lookup: many accounts use email as username in tbl_login.
        user = tbl_login.objects.filter(user_name__iexact=recovery_email).first()

        # Fallback lookup by profile email for Patient/Doctor accounts.
        if not user:
            from adminapp.models import tbl_doctor, tbl_patient
            patient = tbl_patient.objects.filter(email__iexact=recovery_email).select_related('login_id').first()
            doctor = tbl_doctor.objects.filter(email__iexact=recovery_email).select_related('login_id').first()
            if patient and patient.login_id:
                user = patient.login_id
            elif doctor and doctor.login_id:
                user = doctor.login_id

        if not user:
            messages.error(request, 'No account found with this registered email.')
            return render(request, 'Guest/forgot_password.html')

        registered_email = _get_user_email_for_reset(user)
        if not registered_email:
            messages.error(request, 'No recovery email is configured for this account. Please contact support.')
            return render(request, 'Guest/forgot_password.html')

        if registered_email != recovery_email:
            messages.error(request, 'The email does not match our account records.')
            return render(request, 'Guest/forgot_password.html')

        otp = str(random.randint(100000, 999999))
        expires_at = datetime.now() + timedelta(minutes=10)

        request.session['forgot_password_login_id'] = user.login_id
        request.session['forgot_password_otp'] = otp
        request.session['forgot_password_expires_at'] = expires_at.isoformat()

        try:
            from adminapp.utils import send_email
            subject = 'Password Reset OTP - Bloom Moms Care'
            message = (
                f'Dear {user.user_name},\n\n'
                f'Your OTP for password reset is: {otp}\n'
                f'This OTP is valid for 10 minutes.\n\n'
                'If you did not request this, please ignore this email.\n\n'
                'Regards,\n'
                'Bloom Moms Care Team'
            )
            send_email(subject, message, recovery_email)
        except Exception as e:
            _clear_forgot_password_session(request)
            messages.error(request, f'Failed to send OTP email. Please try again. ({str(e)})')
            return render(request, 'Guest/forgot_password.html')

        messages.success(request, 'OTP sent successfully to your registered email.')
        return redirect('guestapp:reset_password')

    return render(request, 'Guest/forgot_password.html')


def reset_password(request):
    login_id = request.session.get('forgot_password_login_id')
    otp_in_session = request.session.get('forgot_password_otp')
    expires_at_raw = request.session.get('forgot_password_expires_at')

    if not login_id or not otp_in_session or not expires_at_raw:
        messages.error(request, 'Password reset session not found. Please request a new OTP.')
        return redirect('guestapp:forgot_password')

    try:
        expires_at = datetime.fromisoformat(expires_at_raw)
    except Exception:
        _clear_forgot_password_session(request)
        messages.error(request, 'Password reset session is invalid. Please try again.')
        return redirect('guestapp:forgot_password')

    if datetime.now() > expires_at:
        _clear_forgot_password_session(request)
        messages.error(request, 'OTP has expired. Please request a new one.')
        return redirect('guestapp:forgot_password')

    if request.method == 'POST':
        entered_otp = request.POST.get('otp', '').strip()
        new_password = request.POST.get('new_password', '').strip()
        confirm_password = request.POST.get('confirm_password', '').strip()

        if entered_otp != otp_in_session:
            messages.error(request, 'Invalid OTP. Please check and try again.')
            return render(request, 'Guest/reset_password.html')

        if len(new_password) < 6:
            messages.error(request, 'Password must be at least 6 characters long.')
            return render(request, 'Guest/reset_password.html')

        if new_password != confirm_password:
            messages.error(request, 'New password and confirm password do not match.')
            return render(request, 'Guest/reset_password.html')

        user = tbl_login.objects.filter(login_id=login_id).first()
        if not user:
            _clear_forgot_password_session(request)
            messages.error(request, 'Account not found. Please contact support.')
            return redirect('guestapp:forgot_password')

        user.password = new_password
        user.save(update_fields=['password'])

        # Keep related profile passwords in sync with login table.
        try:
            from adminapp.models import tbl_doctor, tbl_patient
            if user.role == 'Patient':
                patient = tbl_patient.objects.filter(login_id=user).first()
                if patient:
                    patient.password = new_password
                    patient.save(update_fields=['password'])
            elif user.role == 'Doctor':
                doctor = tbl_doctor.objects.filter(login_id=user).first()
                if doctor:
                    doctor.password = new_password
                    doctor.save(update_fields=['password'])
        except Exception:
            pass

        _clear_forgot_password_session(request)
        messages.success(request, 'Password reset successful. Please login with your new password.')
        return redirect('guestapp:login')

    return render(request, 'Guest/reset_password.html')
