from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from .models import tbl_appointment
from notificationapp.models import Notification
from adminapp.utils import update_trimester_and_notify, ensure_patient_lock_status
from adminapp.models import (
    tbl_patient,
    tbl_doctor,
    tbl_medical_record,
    tbl_prescription
)
from guestapp.models import tbl_login
from doctorapp.models import tbl_visit_history


def _get_patient_with_lock(request):
    """Fetch the logged-in patient and refresh lock status."""
    login_id = request.session.get('login_id')
    patient = get_object_or_404(tbl_patient, login_id=login_id)
    ensure_patient_lock_status(patient)
    return patient


def patientindex(request):
    login_id = request.session.get('login_id')
    unread_count = 0
    
    if login_id:
        try:
            unread_count = Notification.objects.filter(user_type='Patient', user_id=str(login_id), is_read=False).count()
        except Exception:
            pass
    
    return render(request, 'Patient/index.html', {'unread_count': unread_count})

def patient_logout(request):
    request.session.flush()
    messages.success(request, 'You have been logged out successfully.')
    return redirect('guestapp:guestindex')

def about_us(request):
    login_id = request.session.get('login_id')
    unread_count = 0
    
    if login_id:
        try:
            unread_count = Notification.objects.filter(user_type='Patient', user_id=str(login_id), is_read=False).count()
        except Exception:
            pass
    
    return render(request, 'Patient/about.html', {'unread_count': unread_count})

def services(request):
    login_id = request.session.get('login_id')
    unread_count = 0

    if login_id:
        try:
            unread_count = Notification.objects.filter(user_type='Patient', user_id=str(login_id), is_read=False).count()
        except Exception:
            pass

    return render(request, 'Patient/services.html', {'unread_count': unread_count})

def antenatalcare(request):
    login_id = request.session.get('login_id')
    unread_count = 0

    if login_id:
        try:
            unread_count = Notification.objects.filter(user_type='Patient', user_id=str(login_id), is_read=False).count()
        except Exception:
            pass

    return render(request, 'Patient/antenatalcare.html', {'unread_count': unread_count})

def ultrasound(request):
    login_id = request.session.get('login_id')
    unread_count = 0

    if login_id:
        try:
            unread_count = Notification.objects.filter(user_type='Patient', user_id=str(login_id), is_read=False).count()
        except Exception:
            pass

    return render(request, 'Patient/ultrasound.html', {'unread_count': unread_count})

def consultation(request):
    login_id = request.session.get('login_id')
    unread_count = 0

    if login_id:
        try:
            unread_count = Notification.objects.filter(user_type='Patient', user_id=str(login_id), is_read=False).count()
        except Exception:
            pass

    return render(request, 'Patient/consultation.html', {'unread_count': unread_count})

def trimestermonitor(request):
    login_id = request.session.get('login_id')
    unread_count = 0

    if login_id:
        try:
            unread_count = Notification.objects.filter(user_type='Patient', user_id=str(login_id), is_read=False).count()
        except Exception:
            pass

    return render(request, 'Patient/trimestermonitor.html', {'unread_count': unread_count})

def nutritioncare(request):
    login_id = request.session.get('login_id')
    unread_count = 0

    if login_id:
        try:
            unread_count = Notification.objects.filter(user_type='Patient', user_id=str(login_id), is_read=False).count()
        except Exception:
            pass

    return render(request, 'Patient/nutritioncare.html', {'unread_count': unread_count})

def safedelivery(request):
    login_id = request.session.get('login_id')
    unread_count = 0

    if login_id:
        try:
            unread_count = Notification.objects.filter(user_type='Patient', user_id=str(login_id), is_read=False).count()
        except Exception:
            pass

    return render(request, 'Patient/safedelivery.html', {'unread_count': unread_count})

def contact(request):
    login_id = request.session.get('login_id')
    unread_count = 0

    if login_id:
        try:
            unread_count = Notification.objects.filter(user_type='Patient', user_id=str(login_id), is_read=False).count()
        except Exception:
            pass

    return render(request, 'Patient/contact.html', {'unread_count': unread_count})

def trimesterview(request):
    patient = _get_patient_with_lock(request)
    
    # Make sure trimester is updated
    current_trimester = update_trimester_and_notify(patient)

    return render(request, 'Patient/trimesterview.html', {
        'patient': patient,
        'trimester': current_trimester,
        'patient_status': patient.status
    })

def patientdoctorview(request):
    patient = _get_patient_with_lock(request)
    
    # `tbl_patient` model defines the ForeignKey as `doctor_id`,
    # so access the related doctor via `patient.doctor_id`.
    doctor = patient.doctor_id

    return render(request, 'Patient/viewdoctor.html', {
        'doctor': doctor,
        'patient': patient
    })

def appointmentbooking(request):
    from datetime import date
    
    patient = _get_patient_with_lock(request)

    doctors = tbl_doctor.objects.filter(status__iexact='Active')
    
    # Transferred patients cannot book appointments
    if patient.status == 'Transferred':
        messages.error(request, 'Appointment booking is not available for transferred patients.')
        return redirect('patientapp:patientindex')
    
    # Check if patient profile is locked or unlock has expired
    is_locked = patient.profile_lock_status == 'locked'
    if patient.unlock_end_date and date.today() > patient.unlock_end_date:
        is_locked = True

    if request.method == 'POST':
        # Prevent locked patients from booking appointments
        if is_locked:
            messages.warning(request, 'Your profile is locked. Please unlock to book appointments.')
            return redirect('patientapp:appointmentbooking')
        
        appointment_date = request.POST.get('appointment_date')
        appointment_time = request.POST.get('appointment_time')
        reason = request.POST.get('reason')
        doctor_id = request.POST.get('doctor_id')

        selected_doctor = None
        if doctor_id:
            selected_doctor = get_object_or_404(tbl_doctor, pk=doctor_id)
        else:
            selected_doctor = patient.doctor_id

        appointment = tbl_appointment.objects.create(
            patient_id=patient,
            doctor_id=selected_doctor,
            appointment_date=appointment_date,
            appointment_time=appointment_time,
            reason=reason,
            status='Pending'
        )
        
        # Notify all admins
        admin_users = tbl_login.objects.filter(role='Admin')
        for admin in admin_users:
            Notification.objects.create(
                user_type='Admin',
                user_id=str(admin.login_id),
                message=f'Patient {patient.patient_name} booked appointment with Dr. {selected_doctor.doctor_name} on {appointment_date}'
            )

        messages.success(request, f'Appointment booked successfully with Dr. {selected_doctor.doctor_name} for {appointment_date}!')
        return redirect('patientapp:appointmentbooking')

    # Get the patient's consulting doctor if they have one
    selected_doctor = patient.doctor_id if patient.doctor_id else None

    return render(
        request,
        'Patient/appointmentbooking.html',
        {
            'patient': patient,
            'doctors': doctors,
            'selected_doctor': selected_doctor,
            'is_locked': is_locked
        }
    )

def visit_history(request):
    # Use the same session key as other views
    login_id = request.session.get('login_id')
    if not login_id:
        return redirect('patientapp:login')

    # Get the patient object
    patient = _get_patient_with_lock(request)

    # Fetch all visit history
    visit_history_list = tbl_visit_history.objects.filter(
        patient_id=patient
    ).order_by('-visit_date')

    # Latest visit
    latest_visit = visit_history_list.first()

    context = {
        'patient': patient,
        'visit_history': visit_history_list,
        'latest_visit': latest_visit,
    }

    return render(request, 'Patient/visit_history.html', context)

def patient_medical_records(request):
    from datetime import date
    
    # Get logged-in patient
    patient = _get_patient_with_lock(request)
    is_locked = patient.profile_lock_status == 'locked'
    
    # Check if unlock has expired
    if patient.unlock_end_date and date.today() > patient.unlock_end_date:
        is_locked = True
    
    # Check if transferred status - cannot upload
    is_transferred = patient.status == 'Transferred'

    # Fetch all medical records
    records = tbl_medical_record.objects.filter(patient=patient).order_by('-created_at')

    if request.method == 'POST':
        # Transferred patients cannot upload
        if is_transferred:
            messages.warning(request, 'Cannot upload medical records. Your case has been transferred to another facility.')
            return redirect('patientapp:patient_medical_records')
        
        # Locked patients cannot upload new records; they can still view history.
        if is_locked:
            messages.warning(request, 'Your profile is locked. Please unlock to upload new medical records.')
            return redirect('patientapp:patient_medical_records')

        description = request.POST.get('description')
        record_date = request.POST.get('record_date')
        patient_file = request.FILES.get('patient_uploaded_file')

        if description and record_date and patient_file:
            tbl_medical_record.objects.create(
                patient=patient,
                uploaded_by='Patient',
                description=description,
                record_date=record_date,
                patient_uploaded_file=patient_file,
                doctor_view_status=False
            )
            messages.success(request, 'Medical record uploaded successfully!')

        return redirect('patientapp:patient_medical_records')

    return render(
        request,
        'Patient/medical_records.html',
        {
            'patient': patient,
            'records': records,
            'is_locked': is_locked,
            'is_transferred': is_transferred
        }
    )

def patient_prescriptions(request):
    # 🔹 Logged-in patient
    patient = _get_patient_with_lock(request)

    prescriptions = tbl_prescription.objects.filter(
        patient=patient
    ).order_by('-prescription_date')

    context = {
        'patient': patient,
        'prescriptions': prescriptions
    }

    return render(
        request,
        'Patient/prescriptions.html',
        context
    )


def profile_unlock(request):
    """Display unlock plans and process payment for profile unlock."""
    from datetime import date, timedelta
    
    patient = _get_patient_with_lock(request)
    
    # Transferred patients cannot unlock - profile permanently locked
    if patient.status == 'Transferred':
        messages.error(request, 'Profile unlock is not available. Your case has been transferred to another facility.')
        return redirect('patientapp:patientindex')
    
    # Define unlock plans: (duration_months, price_in_currency)
    UNLOCK_PLANS = {
        '1': {'months': 1, 'price': 100, 'label': '1 Month'},
        '3': {'months': 3, 'price': 250, 'label': '3 Months'},
        '6': {'months': 6, 'price': 450, 'label': '6 Months'},
    }
    
    # Check if profile is locked
    is_locked = patient.profile_lock_status == 'locked'
    
    if request.method == 'POST':
        from adminapp.models import tbl_payment
        from datetime import datetime
        
        plan_id = request.POST.get('plan_id')
        payment_status = request.POST.get('payment_status')  # Simulated payment
        payment_method = request.POST.get('payment_method', 'CARD')
        
        if plan_id in UNLOCK_PLANS and payment_status == 'success':
            plan = UNLOCK_PLANS[plan_id]
            
            # Calculate unlock dates
            unlock_start = date.today()
            unlock_end = unlock_start + timedelta(days=30 * plan['months'])
            
            # Update patient profile
            patient.profile_lock_status = 'unlocked'
            patient.unlock_start_date = unlock_start
            patient.unlock_end_date = unlock_end
            patient.save(update_fields=['profile_lock_status', 'unlock_start_date', 'unlock_end_date'])
            
            # Generate unique timestamp for transaction_id
            timestamp = int(datetime.now().timestamp())
            
            # Generate transaction_id based on payment method
            if payment_method == 'CARD':
                transaction_id = f"CARD_{patient.patient_id}_{timestamp}"
            elif payment_method == 'UPI':
                transaction_id = f"UPI_{patient.patient_id}_{timestamp}"
            elif payment_method == 'NETBANKING':
                transaction_id = f"BANK_{patient.patient_id}_{timestamp}"
            else:
                transaction_id = f"TXN_{patient.patient_id}_{timestamp}"
            
            # Create payment record
            try:
                tbl_payment.objects.create(
                    patient=patient,
                    amount=plan['price'],
                    plan_duration=plan['months'],
                    payment_method=payment_method,
                    payment_status='PAID',
                    transaction_id=transaction_id,
                    unlock_start_date=unlock_start,
                    unlock_end_date=unlock_end
                )
            except Exception as e:
                print(f"Error creating payment record: {e}")
            
            # Get the latest payment record that was just created
            latest_payment = tbl_payment.objects.filter(patient=patient).order_by('-payment_id').first()
            
            # Create notification
            try:
                Notification.objects.create(
                    user_type='Patient',
                    user_id=str(patient.login_id.login_id),
                    message=f'Your profile has been unlocked for {plan["label"]}. Your unlock will expire on {unlock_end.strftime("%Y-%m-%d")}.'
                )
                # Notify admin about payment
                admin_users = tbl_login.objects.filter(role='Admin')
                for admin in admin_users:
                    Notification.objects.create(
                        user_type='Admin',
                        user_id=str(admin.login_id),
                        message=f'Patient {patient.patient_name} purchased {plan["label"]} unlock for Rs {plan["price"]}.'
                    )
            except Exception as e:
                print(f"Error creating notifications: {e}")
            
            messages.success(request, f'Profile unlocked successfully for {plan["label"]}! Valid until {unlock_end.strftime("%Y-%m-%d")}.')
            # Pass success flag to show modal
            context = {
                'patient': patient,
                'is_locked': False,
                'plans': UNLOCK_PLANS,
                'unlock_end_date': patient.unlock_end_date,
                'payment_success': True,
                'payment_id': latest_payment.payment_id if latest_payment else None,
                'plan_label': plan['label'],
            }
            return render(request, 'Patient/profile_unlock.html', context)
    
    context = {
        'patient': patient,
        'is_locked': is_locked,
        'plans': UNLOCK_PLANS,
        'unlock_end_date': patient.unlock_end_date,
    }
    
    return render(request, 'Patient/profile_unlock.html', context)


def download_bill(request, payment_id):
    """Generate and download a PDF bill for a payment."""
    from adminapp.models import tbl_payment
    from django.http import HttpResponse
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    from io import BytesIO
    
    # Get payment record
    payment = get_object_or_404(tbl_payment, payment_id=payment_id)
    
    # Verify the logged-in user is the patient
    login_id = request.session.get('login_id')
    if payment.patient.login_id.login_id != int(login_id):
        return HttpResponse("Unauthorized", status=403)
    
    # Create PDF in memory
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
    
    # Container for PDF elements
    elements = []
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#667eea'),
        spaceAfter=6,
        alignment=1  # Center alignment
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=12,
        textColor=colors.HexColor('#333333'),
        spaceAfter=6,
        spaceBefore=12
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#555555'),
        spaceAfter=4
    )
    
    # Title
    elements.append(Paragraph("BLOOM MOMS CARE", title_style))
    elements.append(Paragraph("Maternity Care Management System", styles['Normal']))
    elements.append(Spacer(1, 0.2*inch))
    
    # Bill header
    elements.append(Paragraph("BILL / RECEIPT", heading_style))
    
    # Bill details
    bill_data = [
        ["Bill ID:", f"BILL-{payment.payment_id}"],
        ["Bill Date:", payment.created_at.strftime("%d-%m-%Y")],
        ["Bill Time:", payment.created_at.strftime("%H:%M:%S")],
    ]
    
    bill_table = Table(bill_data, colWidths=[2*inch, 3.5*inch])
    bill_table.setStyle(TableStyle([
        ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 10),
        ('FONT', (1, 0), (1, -1), 'Helvetica', 10),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#333333')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(bill_table)
    elements.append(Spacer(1, 0.2*inch))
    
    # Patient Information
    elements.append(Paragraph("PATIENT INFORMATION", heading_style))
    
    doctor_name = payment.patient.doctor_id.doctor_name if payment.patient.doctor_id else "N/A"
    
    patient_data = [
        ["Patient Name:", payment.patient.patient_name],
        ["Patient ID:", str(payment.patient.patient_id)],
        ["Age:", str(payment.patient.age)],
        ["Assigned Doctor:", f"Dr {doctor_name}"],
    ]
    
    patient_table = Table(patient_data, colWidths=[2*inch, 3.5*inch])
    patient_table.setStyle(TableStyle([
        ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 10),
        ('FONT', (1, 0), (1, -1), 'Helvetica', 10),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#333333')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(patient_table)
    elements.append(Spacer(1, 0.2*inch))
    
    # Payment Details
    elements.append(Paragraph("PAYMENT DETAILS", heading_style))
    
    plan_labels = {1: '1 Month', 3: '3 Months', 6: '6 Months'}
    plan_label = plan_labels.get(payment.plan_duration, f'{payment.plan_duration} months')
    service_description = f"Profile Unlock - {plan_label} Access"
    
    payment_data = [
        ["Service Description:", service_description],
        ["Amount Paid:", f"₹ {float(payment.amount):.2f}"],
        ["Payment Mode:", payment.get_payment_method_display()],
        ["Payment Date:", payment.created_at.strftime("%d-%m-%Y")],
        ["Transaction ID:", payment.transaction_id],
        ["Payment Status:", "PAID"],
    ]
    
    payment_table = Table(payment_data, colWidths=[2*inch, 3.5*inch])
    payment_table.setStyle(TableStyle([
        ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 10),
        ('FONT', (1, 0), (1, -1), 'Helvetica', 10),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#333333')),
        ('TEXTCOLOR', (1, 4), (1, 4), colors.HexColor('#27ae60')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(payment_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Footer
    elements.append(Paragraph("Thank you for choosing Bloom Moms Care!", styles['Normal']))
    elements.append(Paragraph("For support, contact us at support@bloommoms.com", styles['Normal']))
    
    # Build PDF
    doc.build(elements)
    
    # Get PDF data
    buffer.seek(0)
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="bill_{payment.payment_id}.pdf"'
    
    return response
