

# Create your views here.
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django import forms
from django.contrib import messages
from notificationapp.models import Notification
from patientapp.models import tbl_appointment
from .models import *
from datetime import date, timedelta
from django.shortcuts import render, redirect
from adminapp.utils import update_trimester_and_notify
from openpyxl import Workbook
from openpyxl.styles import Font
from django.db.models import Count, Max

# Create your views here.
# adminapp/views.py
from django.shortcuts import render, redirect

from guestapp.models import tbl_login

def admin_login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            # Check login for admin role and active status
            user = tbl_login.objects.get(
                user_name=username,
                password=password,
                role='Admin',
                status='Active'
            )
            # Set session
            request.session['login_id'] = user.login_id
            request.session['role'] = user.role
            request.session['is_admin'] = True

            messages.success(request, 'Welcome back! You have successfully logged in.')
            return redirect('adminapp:adminindex') 
        except tbl_login.DoesNotExist:
            messages.error(request, 'Invalid credentials or not an admin.')
            return render(request, 'Admin/index.html')

    return render(request, 'Admin/index.html')

def admin_logout(request):
    request.session.flush()
    messages.success(request, 'You have been logged out successfully.')
    return redirect('guestapp:guestindex')

def adminindex(request):
    import json
    from django.db.models import Count
    from django.db.models.functions import TruncMonth
    
    login_id = request.session.get('login_id')
    unread_count = 0
    today = date.today()
    
    # Dashboard counts
    todays_appointments = tbl_appointment.objects.filter(appointment_date=today).count()
    total_patients = tbl_patient.objects.count()
    total_doctors = tbl_doctor.objects.filter(status__iexact='active').count()
    total_payments = tbl_payment.objects.filter(payment_status='PAID').count()
    
    # Monthly patient registration trend (last 6 months)
    from datetime import timedelta
    six_months_ago = today - timedelta(days=180)
    monthly_registrations = tbl_patient.objects.filter(
        created_at__gte=six_months_ago
    ).annotate(
        month=TruncMonth('created_at')
    ).values('month').annotate(
        count=Count('patient_id')
    ).order_by('month')
    
    # Format for chart
    months_data = []
    counts_data = []
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    for record in monthly_registrations:
        if record['month']:
            months_data.append(month_names[record['month'].month - 1])
            counts_data.append(record['count'])
    
    # Doctor-wise workload report
    doctors = tbl_doctor.objects.filter(status__iexact='active')
    doctor_workload_data = []
    doctor_names_chart = []
    patient_counts_chart = []
    
    for doctor in doctors:
        # Count assigned patients
        assigned_patients = tbl_patient.objects.filter(doctor_id=doctor.doctor_id).count()
        
        # Count today's appointments
        today_appointments = tbl_appointment.objects.filter(
            doctor_id=doctor.doctor_id,
            appointment_date=today
        ).count()
        
        # Determine status
        status = "Available" if today_appointments < 5 else "Busy"
        
        doctor_workload_data.append({
            'name': doctor.doctor_name,
            'assigned_patients': assigned_patients,
            'today_appointments': today_appointments,
            'status': status
        })
        
        doctor_names_chart.append(doctor.doctor_name)
        patient_counts_chart.append(assigned_patients)
    
    # Appointment Status Distribution for Pie Chart
    accepted_count = tbl_appointment.objects.filter(status='Accepted').count()
    rescheduled_count = tbl_appointment.objects.filter(status='Rescheduled').count()
    pending_count = tbl_appointment.objects.filter(status='Pending').count()
    
    # Patient Distribution by Trimester for Pie Chart
    first_trimester_count = tbl_patient.objects.filter(current_trimester=1).count()
    second_trimester_count = tbl_patient.objects.filter(current_trimester=2).count()
    third_trimester_count = tbl_patient.objects.filter(current_trimester=3).count()
    
    if login_id:
        try:
            # Show all unread admin notifications (all admins need to see important updates)
            unread_count = Notification.objects.filter(user_type='Admin', is_read=False).count()
        except Exception:
            pass
    
    return render(
        request,
        'Admin/index.html',
        {
            'unread_count': unread_count,
            'today': today,
            'todays_appointments': todays_appointments,
            'total_patients': total_patients,
            'total_doctors': total_doctors,
            'total_payments': total_payments,
            'monthly_registrations': list(monthly_registrations),
            'months_labels_json': json.dumps(months_data),
            'registration_counts_json': json.dumps(counts_data),
            'months_labels': months_data,
            'registration_counts': counts_data,
            'doctor_workload': doctor_workload_data,
            'doctor_names_json': json.dumps(doctor_names_chart),
            'patient_counts_json': json.dumps(patient_counts_chart),
            'accepted_count': accepted_count,
            'rescheduled_count': rescheduled_count,
            'pending_count': pending_count,
            'first_trimester_count': first_trimester_count,
            'second_trimester_count': second_trimester_count,
            'third_trimester_count': third_trimester_count
        }
    )

def export_patient_report(request):
    patients = tbl_patient.objects.select_related('doctor_id').all()

    appointment_stats = tbl_appointment.objects.values('patient_id').annotate(
        total_appointments=Count('appointment_id'),
        last_visit_date=Max('appointment_date')
    )

    appointment_map = {
        item['patient_id']: {
            'total_appointments': item['total_appointments'],
            'last_visit_date': item['last_visit_date']
        }
        for item in appointment_stats
    }

    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = 'Patient_Report'

    headers = [
        'Patient ID',
        'Patient Name',
        'Age',
        'Assigned Doctor Name',
        'Trimester Status',
        'Number of Appointments',
        'Last Visit Date'
    ]

    worksheet.append(headers)
    for cell in worksheet[1]:
        cell.font = Font(bold=True)

    for patient in patients:
        stats = appointment_map.get(patient.patient_id, {})
        total_appointments = stats.get('total_appointments', 0)
        last_visit_date = stats.get('last_visit_date')

        if patient.delivery_date:
            trimester_status = 'Delivered'
        else:
            if patient.current_trimester == 1:
                trimester_status = '1'
            elif patient.current_trimester == 2:
                trimester_status = '2'
            elif patient.current_trimester == 3:
                trimester_status = '3'
            else:
                trimester_status = 'N/A'

        if last_visit_date:
            last_visit_display = last_visit_date.strftime('%Y-%m-%d')
        else:
            last_visit_display = 'N/A'

        if patient.doctor_id and patient.doctor_id.doctor_name:
            doctor_name = f"Dr {patient.doctor_id.doctor_name}"
        else:
            doctor_name = 'N/A'

        worksheet.append([
            patient.patient_id,
            patient.patient_name,
            patient.age,
            doctor_name,
            trimester_status,
            total_appointments,
            last_visit_display
        ])

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="patient_report.xlsx"'
    workbook.save(response)

    return response
def districtreg(request):
    if request.method == 'POST':
        district_name = request.POST.get('districtname')
        district_obj= tbl_district()
        district_obj.district_name = district_name
        district_obj.save()
        messages.success(request, f'District "{district_name}" added successfully!')
        return redirect('adminapp:viewdistrict')
    return render(request, 'Admin/districtreg.html')
def viewdistrict(request):
    dist = tbl_district.objects.all()
    return render(request, 'Admin/viewdistrict.html', {'dist': dist})
def deletedistrict(request, id):
    dist= tbl_district.objects.get(district_id=id)
    district_name = dist.district_name
    dist.delete()
    messages.success(request, f'District "{district_name}" deleted successfully!')
    return redirect('adminapp:viewdistrict')
def editdistrict(request, id):
    if request.method == 'POST':
        district_name = request.POST.get('districtname')
        dist= tbl_district.objects.get(district_id=id)
        dist.district_name = district_name
        dist.save()
        messages.success(request, f'District updated to "{district_name}" successfully!')
        return redirect('adminapp:viewdistrict')
    dist= tbl_district.objects.get(district_id=id)
    return render(request, 'Admin/editdistrict.html', {'dist': dist})
    


def countryreg(request):
    if request.method == 'POST':
        country_name = request.POST.get('countryname')
        country_obj= tbl_country()
        country_obj.country_name = country_name
        country_obj.save()
        messages.success(request, f'Country "{country_name}" added successfully!')
    return render(request, 'Admin/countryreg.html')


def doctorreg(request):
    if request.method == 'POST':
        lob = tbl_login()
        lob.user_name = request.POST.get("demail")
        lob.password = request.POST.get("pw")
        lob.role = "Doctor"
        lob.status="active"
        if tbl_login.objects.filter(user_name=request.POST.get("demail")).exists():
            messages.error(request, 'Email already exists. Please use a different email.')
            return redirect('adminapp:doctorreg')
        else:
            doctor_name = request.POST.get('doctorname')
            email= request.POST.get('demail')
            password=request.POST.get('pw')
            specialization= request.POST.get('specialization')
            experience= request.POST.get('experience')
            phone= request.POST.get('contact')
            hospital_timimg= request.POST.get('timing')
            img = request.FILES.get('dimage')

        lob.save()
        doctor_obj= tbl_doctor()
        doctor_obj.doctor_name = doctor_name
        doctor_obj.email = email
        doctor_obj.password = password
        doctor_obj.specialization = specialization
        doctor_obj.experience = experience
        doctor_obj.phone = phone
        doctor_obj.hospital_timimg = hospital_timimg
        doctor_obj.status = 'active'
        doctor_obj.created_at = date.today()
        doctor_obj.image = img
        doctor_obj.login_id = lob
        doctor_obj.save()
        
        # Send welcome email after successful registration
        from adminapp.utils import send_email
        subject = "Welcome to Bloom Moms Care - Doctor Account Created"
        message = f"""Dear Dr. {doctor_name},

Welcome to Bloom Moms Care! Your doctor account has been successfully created.

Your Login Credentials:
Username: {email}
Password: {password}

You can now log in to the system and start managing your patients and appointments.

Best regards,
Bloom Moms Care Team"""
        send_email(subject, message, email)
        messages.success(request, f'Doctor "{doctor_name}" registered successfully! Login credentials sent to {email}.')
        return redirect('adminapp:viewdoctors')
        
    return render(request, 'Admin/doctorreg.html')

def viewdoctors(request):
    doc = tbl_doctor.objects.all()
    return render(request, 'Admin/viewdoctors.html', {'doc': doc})
def editdoctor(request, id):
    doc = tbl_doctor.objects.get(doctor_id=id)
    
    if request.method == 'POST':
        doctor_name = request.POST.get('doctorname')
        email= request.POST.get('email')
        specialization= request.POST.get('specialization')
        experience= request.POST.get('experience')
        phone= request.POST.get('contact')
        hospital_timimg= request.POST.get('timing')
        status = request.POST.get('status')
        password = request.POST.get('pw')

        doc.doctor_name = doctor_name
        doc.email = email
        doc.specialization = specialization
        doc.experience = experience
        doc.phone = phone
        doc.hospital_timimg = hospital_timimg
        doc.status = status
        
        # Update password if provided
        if password:
            doc.password = password
        
        # Handle image upload if provided
        if 'dimage' in request.FILES:
            doc.image = request.FILES['dimage']
        
        doc.save()
        messages.success(request, f'Doctor "{doctor_name}" updated successfully!')
        return redirect('adminapp:viewdoctors')
    
    return render(request, 'Admin/editdoctor.html', {'doc': doc})

def deletedoctor(request, id):
    doc = tbl_doctor.objects.get(doctor_id=id)
    doctor_name = doc.doctor_name
    
    # Delete associated login record if it exists
    if doc.login_id:
        try:
            doc.login_id.delete()
        except Exception as e:
            pass  # Login record might already be deleted
    
    doc.delete()
    messages.success(request, f'Doctor "{doctor_name}" removed successfully!')
    return redirect('adminapp:viewdoctors')


def deactivatedoctor(request, id):
    doc = get_object_or_404(tbl_doctor, doctor_id=id)

    doc.status = 'inactive'
    doc.save(update_fields=['status'])

    if doc.login_id:
        doc.login_id.status = 'inactive'
        doc.login_id.save(update_fields=['status'])

    messages.success(request, f'Doctor "{doc.doctor_name}" deactivated successfully!')
    return redirect('adminapp:viewdoctors')


def activatedoctor(request, id):
    doc = get_object_or_404(tbl_doctor, doctor_id=id)

    doc.status = 'active'
    doc.save(update_fields=['status'])

    if doc.login_id:
        doc.login_id.status = 'active'
        doc.login_id.save(update_fields=['status'])

    messages.success(request, f'Doctor "{doc.doctor_name}" activated successfully!')
    return redirect('adminapp:viewdoctors')

def patientreg(request):
    doc= tbl_doctor.objects.all()
    if request.method == 'POST':
        lob = tbl_login()
        lob.user_name = request.POST.get("pemail")
        lob.password = request.POST.get("pw")
        lob.role = "Patient"
        lob.status="active"
        if tbl_login.objects.filter(user_name=request.POST.get("pemail")).exists():
            messages.error(request, 'Email already exists. Please use a different email.')
            return redirect('adminapp:patientreg')
        else:
            patient_name = request.POST.get('patientname')
            email= request.POST.get('pemail')
            age= request.POST.get('age')
            did= request.POST.get('ddldoctor')
            phone= request.POST.get('contact')
            address= request.POST.get('address')
            blood_group= request.POST.get('bgroup')
            last_cycle_date= request.POST.get('lcd')
            img = request.FILES.get('pimage')

        lob.save()
        patient_obj= tbl_patient()
        selected_doctor = tbl_doctor.objects.get(doctor_id=did)
        patient_obj.doctor_id = selected_doctor
        patient_obj.patient_name = patient_name
        patient_obj.email = email
        patient_obj.password = lob.password
        patient_obj.age = age
        patient_obj.phone = phone
        patient_obj.address = address
        patient_obj.blood_group = blood_group
        
        # Parse and save last cycle date
        from datetime import datetime
        lcd_obj = datetime.strptime(last_cycle_date, '%Y-%m-%d').date()
        patient_obj.last_cycle_date = lcd_obj
        
        # Auto-calculate EDD (LCD + 280 days)
        patient_obj.edd_date = lcd_obj + timedelta(days=280)
        patient_obj.status = 'active'
        patient_obj.created_at = date.today()
        patient_obj.image = img
        patient_obj.login_id = lob
        patient_obj.save()
        # update trimester immediately after saving last_cycle_date
        try:
            update_trimester_and_notify(patient_obj)
        except Exception:
            pass
        
        # Send welcome email after successful registration
        from adminapp.utils import send_email
        subject = "Welcome to Bloom Moms Care"
        message = f"""Dear {patient_name},

Welcome to Bloom Moms Care! Your account has been successfully created.

Your Login Credentials:
Username: {email}
Password: {lob.password}

Your assigned doctor: Dr. {selected_doctor.doctor_name}

You can now log in with your credentials and access your medical records, appointments, and other features.

Best regards,
Bloom Moms Care Team"""
        send_email(subject, message, email)
        messages.success(request, f'Patient "{patient_name}" registered successfully! Login credentials sent to {email}.')
        return redirect('adminapp:viewpatients')
        
    return render(request, 'Admin/patientreg.html',{"doc": doc})
def viewpatients(request):
    pat = tbl_patient.objects.all()
    return render(request, 'Admin/viewpatients.html', {'pat': pat})
def editpatient(request, id):
    doc= tbl_doctor.objects.all()
    if request.method == 'POST':
        patient_name = request.POST.get('patientname')
        email= request.POST.get('pemail')
        age= request.POST.get('age')
        did= request.POST.get('ddldoctor')
        phone= request.POST.get('contact')
        address= request.POST.get('address')
        blood_group= request.POST.get('bgroup')
        last_cycle_date= request.POST.get('lcd')

        pat= tbl_patient.objects.get(patient_id=id)
        selected_doctor = tbl_doctor.objects.get(doctor_id=did)
        pat.doctor_id = selected_doctor
        pat.patient_name = patient_name
        pat.email = email
        pat.age = age
        pat.phone = phone
        pat.address = address
        pat.blood_group = blood_group
        
        # Parse and save last cycle date
        from datetime import datetime
        lcd_obj = datetime.strptime(last_cycle_date, '%Y-%m-%d').date()
        pat.last_cycle_date = lcd_obj
        
        # Auto-calculate EDD (LCD + 280 days)
        pat.edd_date = lcd_obj + timedelta(days=280)
        pat.save()
        # update trimester after editing last_cycle_date
        try:
            update_trimester_and_notify(pat)
        except Exception:
            pass
        messages.success(request, f'Patient "{patient_name}" updated successfully!')
        return redirect('adminapp:viewpatients')
    pat= tbl_patient.objects.get(patient_id=id)
    return render(request, 'Admin/editpatient.html', {'pat': pat,"doc": doc})

def deletepatient(request, id):
    pat = tbl_patient.objects.get(patient_id=id)
    patient_name = pat.patient_name
    loginid = pat.login_id_id
    lob = tbl_login.objects.get(login_id=loginid)
    lob.delete()
    pat.delete()
    messages.success(request, f'Patient "{patient_name}" removed successfully!')
    return redirect('adminapp:viewpatients')

def view_appointments(request):
    appointments = tbl_appointment.objects.all().order_by('-created_at')
    return render(request, 'Admin/appointmentview.html', {
        'appointments': appointments
    })
def accept_appointment(request, id):
    appointment = tbl_appointment.objects.get(appointment_id=id)
    appointment.status = 'Accepted'
    appointment.save()
    
    # Notify patient
    Notification.objects.create(
        user_type='Patient',
        user_id=str(appointment.patient_id.login_id.login_id),
        message=f'Your appointment with Dr. {appointment.doctor_id.doctor_name} has been accepted'
    )
    
    # Notify doctor
    Notification.objects.create(
        user_type='Doctor',
        user_id=str(appointment.doctor_id.login_id.login_id),
        message=f'Appointment with {appointment.patient_id.patient_name} on {appointment.appointment_date} has been accepted'
    )
    
    # Send acceptance email to patient
    from adminapp.utils import send_email
    subject = "Appointment Accepted"
    message = f"""Dear {appointment.patient_id.patient_name},

Your appointment has been accepted by the administrator.

Appointment Details:
Date: {appointment.appointment_date}
Time: {appointment.appointment_time}
Doctor: Dr. {appointment.doctor_id.doctor_name}
Reason: {appointment.reason}

Please arrive 10 minutes before your scheduled appointment time.

Best regards,
Bloom Moms Care Team"""
    send_email(subject, message, appointment.patient_id.email)
    
    # Send confirmation email to doctor
    subject_doc = "Appointment Confirmed"
    message_doc = f"""Dear Dr. {appointment.doctor_id.doctor_name},

An appointment has been confirmed for you.

Patient: {appointment.patient_id.patient_name}
Date: {appointment.appointment_date}
Time: {appointment.appointment_time}
Reason: {appointment.reason}

Please be available at the scheduled time.

Best regards,
Bloom Moms Care Team"""
    send_email(subject_doc, message_doc, appointment.doctor_id.email)
    messages.success(request, f'Appointment with {appointment.patient_id.patient_name} accepted successfully!')
    
    return redirect('adminapp:view_appointments')
def reschedule_appointment(request, id):
    # Get the appointment object safely
    appointment = get_object_or_404(tbl_appointment, appointment_id=id)

    if request.method == 'POST':
        # Get values from form; convert empty strings to None
        reschedule_date = request.POST.get('reschedule_date') or None
        reschedule_time = request.POST.get('reschedule_time') or None
        admin_note = request.POST.get('admin_note') or ''

        # Update appointment fields
        appointment.reschedule_date = reschedule_date
        appointment.reschedule_time = reschedule_time
        appointment.admin_note = admin_note
        appointment.status = 'Rescheduled'
        appointment.save()
        
        # Notify patient
        Notification.objects.create(
            user_type='Patient',
            user_id=str(appointment.patient_id.login_id.login_id),
            message=f'Your appointment has been rescheduled to {reschedule_date}'
        )
        
        # Notify doctor
        Notification.objects.create(
            user_type='Doctor',
            user_id=str(appointment.doctor_id.login_id.login_id),
            message=f'Appointment with {appointment.patient_id.patient_name} has been rescheduled to {reschedule_date}'
        )
        
        # Send rescheduling email to patient
        from adminapp.utils import send_email
        subject = "Appointment Rescheduled"
        message = f"""Dear {appointment.patient_id.patient_name},

Your appointment has been rescheduled.

New Appointment Details:
Date: {reschedule_date}
Time: {reschedule_time}
Doctor: Dr. {appointment.doctor_id.doctor_name}
Reason: {appointment.reason}
{'Admin Note: ' + admin_note if admin_note else ''}

Please arrive 10 minutes before your scheduled appointment time.

Best regards,
Bloom Moms Care Team"""
        send_email(subject, message, appointment.patient_id.email)
        
        # Send rescheduling email to doctor
        subject_doc = "Appointment Rescheduled"
        message_doc = f"""Dear Dr. {appointment.doctor_id.doctor_name},

An appointment with a patient has been rescheduled.

Patient: {appointment.patient_id.patient_name}
New Date: {reschedule_date}
New Time: {reschedule_time}
Reason: {appointment.reason}

Please be available at the new scheduled time.

Best regards,
Bloom Moms Care Team"""
        send_email(subject_doc, message_doc, appointment.doctor_id.email)
        messages.success(request, f'Appointment with {appointment.patient_id.patient_name} rescheduled to {reschedule_date}!')

        return redirect('adminapp:view_appointments')

    # If GET request, render the reschedule form
    return render(request, 'Admin/reschedule.html', {
        'appointment': appointment
    })

def doctorleave(request):
    from .models import tbl_doctor, tbl_doctor_leave
    from patientapp.models import tbl_appointment
    doctors = tbl_doctor.objects.filter(status='active')

    if request.method == 'POST':
        doctor_id = request.POST.get('doctor')
        leave_date = request.POST.get('leave_date')
        reason = request.POST.get('reason')

        tbl_doctor_leave.objects.create(
            doctor_id=doctor_id,
            leave_date=leave_date,
            reason=reason
        )

        appointments = tbl_appointment.objects.filter(
            doctor_id=doctor_id,
            appointment_date=leave_date,
            status__in=['Accepted', 'Rescheduled']
        )

        for app in appointments:
            app.status = "Doctor Unavailable"
            app.admin_note = "Doctor is on leave"
            app.save()

        messages.success(request, f'Doctor leave recorded successfully for {leave_date}!')
        return redirect('adminapp:viewdoctorleave')

    return render(request, 'Admin/docleave.html', {
        'doctors': doctors
    })


def viewdoctorleave(request):
    selected_date = request.GET.get('leave_date')
    if not selected_date:
        selected_date = date.today().isoformat()

    leaves = tbl_doctor_leave.objects.select_related('doctor').filter(
        leave_date=selected_date
    ).order_by('-leave_date')

    return render(request, 'Admin/docleaveview.html', {
        'leaves': leaves,
        'selected_date': selected_date
    })
from django.shortcuts import render, redirect, get_object_or_404
from adminapp.models import tbl_patient, tbl_medical_record

def upload_medical_record(request, patient_id):
    patient = get_object_or_404(tbl_patient, patient_id=patient_id)

    if request.method == 'POST':
        description = request.POST.get('description')
        file = request.FILES.get('file')

        tbl_medical_record.objects.create(
            patient=patient,
            uploaded_by='Admin',
            description=description,
            admin_uploaded_file=file
        )
        messages.success(request, f'Medical record uploaded successfully for {patient.patient_name}!')
        return redirect('adminapp:view_patient', patient_id=patient.patient_id)

    return render(request, 'Admin/upload_medical_record.html', {'patient': patient})

def select_doctor(request):
    doctors = tbl_doctor.objects.filter(status='active')
    return render(request, 'Admin/select_doctor.html', {
        'doctors': doctors
    })



def doctor_patients(request, doctor_id):
    doctor = get_object_or_404(tbl_doctor, doctor_id=doctor_id)

    patients = tbl_patient.objects.filter(
        doctor_id=doctor
    )

    return render(request, 'Admin/patientview.html', {
        'doctor': doctor,
        'patients': patients
    })

from django.shortcuts import render, redirect, get_object_or_404
from adminapp.models import tbl_patient, tbl_medical_record,tbl_prescription




def admin_patient_profile(request, patient_id):
    # Get patient
    patient = get_object_or_404(tbl_patient, patient_id=patient_id)
    is_transferred = patient.status == 'Transferred'

    # Medical records (admin + patient uploads)
    records = tbl_medical_record.objects.filter(
        patient=patient
    ).order_by('-created_at')

    # 🔹 PRESCRIPTIONS (ADMIN VIEW ONLY)
    prescriptions = tbl_prescription.objects.filter(
        patient=patient
    ).order_by('-created_at')

    # Handle admin medical record upload
    if request.method == 'POST':
        if is_transferred:
            messages.warning(request, 'Medical record upload is not allowed for transferred patients.')
            return redirect('adminapp:admin_patient_profile', patient_id=patient_id)

        description = request.POST.get('description')
        record_date = request.POST.get('record_date')
        admin_file = request.FILES.get('admin_uploaded_file')

        if description and record_date and admin_file:
            tbl_medical_record.objects.create(
                patient=patient,
                uploaded_by='Admin',
                description=description,
                record_date=record_date,
                admin_uploaded_file=admin_file,
                doctor_view_status=False
            )
            messages.success(request, f'Medical record added successfully for {patient.patient_name}!')

        # Prevent form resubmission
        return redirect('adminapp:admin_patient_profile', patient_id=patient_id)

    # Context for template
    context = {
        'patient': patient,
        'records': records,
        'prescriptions': prescriptions,
        'is_transferred': is_transferred
    }

    return render(request, 'Admin/patient_profile.html', context)
