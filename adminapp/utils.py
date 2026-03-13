from datetime import date, datetime, timedelta
from doctorapp.models import tbl_trimester_update
from adminapp.models import tbl_patient


def calculate_trimester(last_cycle_date):
    # normalize input: accept date objects or common string formats
    if not last_cycle_date:
        return 1

    if isinstance(last_cycle_date, str):
        parsed = None
        for fmt in ('%Y-%m-%d', '%d-%m-%Y', '%d/%m/%Y'):
            try:
                parsed = datetime.strptime(last_cycle_date, fmt).date()
                break
            except ValueError:
                continue
        if not parsed:
            # fallback: try ISO fromfromisoformat
            try:
                parsed = date.fromisoformat(last_cycle_date)
            except Exception:
                raise ValueError(f"Unrecognized date format: {last_cycle_date}")
        last_cycle_date = parsed

    if last_cycle_date > date.today():
        return 1

    weeks = (date.today() - last_cycle_date).days // 7

    if weeks < 13:
        return 1
    elif weeks < 28:
        return 2
    else:
        return 3


def update_trimester_and_notify(patient):
    if not can_update_trimester(patient):
        return patient.current_trimester

    if not patient.last_cycle_date:
        return patient.current_trimester  

    new_trimester = calculate_trimester(patient.last_cycle_date)

    
    if patient.current_trimester != new_trimester:
        patient.current_trimester = new_trimester
        patient.save()

        tbl_trimester_update.objects.create(
            patient_id=patient,
            trimester_number=new_trimester,
            title=f"Entered Trimester {new_trimester}",
            description=(
                f"You have entered trimester {new_trimester}. "
                f"Please follow medical guidance."
            )
        )

    return new_trimester


def update_all_patients_trimester():
    patients = tbl_patient.objects.all()
    for patient in patients:
        update_trimester_and_notify(patient)
    return "Trimester update process completed."


# Lock a patient profile 6 months after the recorded delivery date.
LOCK_DURATION_DAYS = 180


def ensure_patient_lock_status(patient):
    """Return True if the patient profile is locked; update fields when needed. Also triggers notification when lock is first applied."""
    
    # First, check if unlock period has expired
    if patient.unlock_end_date and date.today() > patient.unlock_end_date:
        # Unlock period has expired, revert to locked status
        patient.profile_lock_status = 'locked'
        patient.unlock_start_date = None
        patient.unlock_end_date = None
        patient.save(update_fields=['profile_lock_status', 'unlock_start_date', 'unlock_end_date'])
        
        # Send notification about expiry
        try:
            from notificationapp.models import Notification
            Notification.objects.create(
                user_type='Patient',
                user_id=str(patient.login_id.login_id),
                message='Your unlock period has expired. Your profile is now locked again.'
            )
        except Exception as e:
            print(f"Error sending unlock expiry notification: {e}")
    
    # If currently unlocked and valid, return False (not locked)
    if patient.profile_lock_status == 'unlocked' and patient.unlock_end_date:
        if date.today() <= patient.unlock_end_date:
            return False  # Profile is unlocked and valid
    
    if not patient.delivery_date:
        # No delivery recorded, keep profile unlocked.
        if patient.profile_lock_status == 'locked':
            patient.profile_lock_status = 'unlocked'
            patient.lock_start_date = None
            patient.save(update_fields=['profile_lock_status', 'lock_start_date'])
        return False

    lock_date = patient.delivery_date + timedelta(days=LOCK_DURATION_DAYS)
    is_locked = date.today() >= lock_date

    if is_locked and patient.profile_lock_status != 'locked':
        # Only lock if unlock period is not active
        if not patient.unlock_end_date or date.today() > patient.unlock_end_date:
            patient.profile_lock_status = 'locked'
            patient.lock_start_date = lock_date
            patient.save(update_fields=['profile_lock_status', 'lock_start_date'])
            
            # Send notification when patient profile gets locked
            try:
                from notificationapp.models import Notification
                Notification.objects.create(
                    user_type='Patient',
                    user_id=str(patient.login_id.login_id),
                    message='Your profile has been locked 6 months after delivery. You can view records but cannot upload new ones. You can unlock your profile with a payment plan.'
                )
            except Exception as e:
                print(f"Error sending lock notification: {e}")
            
    elif not is_locked and patient.profile_lock_status == 'locked':
        # Allow automatic unlock if delivery date was corrected.
        patient.profile_lock_status = 'unlocked'
        patient.lock_start_date = None
        patient.save(update_fields=['profile_lock_status', 'lock_start_date'])

    return patient.profile_lock_status == 'locked'


def send_email(subject, message, recipient_email):
    """
    Send plain text email using Django's send_mail function.
    
    Args:
        subject (str): Email subject
        message (str): Email body (plain text)
        recipient_email (str): Recipient's email address
    
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    from django.core.mail import send_mail
    from django.conf import settings
    
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient_email],
            fail_silently=False
        )
        return True
    except Exception as e:
        print(f"Error sending email to {recipient_email}: {str(e)}")
        return False


# ======================== STATUS-BASED LOGIC ========================

def can_add_prescription(patient):
    """
    Check if a prescription can be added to a patient.
    
    Restricted for: Miscarriage, Transferred
    Allowed for: Active, Delivered, Emergency
    """
    if patient.status in ['Miscarriage', 'Transferred']:
        return False
    return True


def can_update_trimester(patient):
    """
    Check if trimester can be updated for a patient.
    
    Restricted for: Miscarriage, Transferred, Delivered, Emergency
    Allowed for: Active
    """
    if patient.status in ['Miscarriage', 'Transferred', 'Delivered', 'Emergency']:
        return False
    return True


def is_patient_profile_readonly(patient):
    """
    Check if patient profile should be read-only.
    
    Readonly for: Transferred, Miscarriage (after 6 months)
    Editable for: Active, Delivered, Emergency, Miscarriage (within 6 months)
    """
    if patient.status == 'Transferred':
        return True
    
    if patient.status == 'Miscarriage':
        # Check if 6 months have passed since miscarriage
        if patient.miscarriage_date:
            lockout_date = patient.miscarriage_date + timedelta(days=180)
            if date.today() >= lockout_date:
                return True  # Lock after 6 months
    
    return False


def get_status_restrictions(status):
    """
    Get human-readable restrictions for a given patient status.
    """
    restrictions = {
        'Active': 'No restrictions. Full access to medical records and prescriptions.',
        'Delivered': 'Patient has been delivered. Profile can be updated by doctors.',
        'Miscarriage': 'Your profile will remain accessible for 6 months of recovery. Prescriptions and trimester updates are disabled. After 6 months, the profile will be locked automatically.',
        'Emergency': 'Emergency case. All updates allowed. Profile highlighted with alert.',
        'Transferred': 'Patient transferred to another hospital. Profile is immediately locked. No prescriptions, trimester updates, or medical record uploads allowed. All existing records remain viewable.',
    }
    return restrictions.get(status, 'Unknown status')


def get_miscarriage_lockout_info(patient):
    """
    Get information about miscarriage lockout status.
    Returns: {is_locked, days_remaining, lockout_date, message}
    """
    if patient.status != 'Miscarriage' or not patient.miscarriage_date:
        return None
    
    lockout_date = patient.miscarriage_date + timedelta(days=180)
    days_remaining = (lockout_date - date.today()).days
    is_locked = date.today() >= lockout_date
    
    if is_locked:
        message = "Your profile has been locked for recovery. Please contact your doctor if you need assistance."
    else:
        message = f"Your profile will be automatically locked in {max(0, days_remaining)} days for your recovery period."
    
    return {
        'is_locked': is_locked,
        'days_remaining': max(0, days_remaining),
        'lockout_date': lockout_date,
        'message': message
    }

    """
    Check if user role can update patient status.
    
    Only: Doctor, Admin
    Cannot: Patient
    """
    if login_role in ['Doctor', 'Admin']:
        return True
    return False


def check_role_can_add_notes(login_role):
    """
    Check if user role can add medical notes (miscarriage, emergency, transfer).
    
    Only: Doctor
    Cannot: Admin, Patient
    """
    if login_role == 'Doctor':
        return True
    return False


def log_status_change(patient, old_status, new_status, notes=""):
    """
    Log a patient status change for audit trail.
    """
    try:
        from django.db import connection
        from datetime import datetime
        
        log_entry = {
            'patient_id': patient.patient_id,
            'patient_name': patient.patient_name,
            'old_status': old_status,
            'new_status': new_status,
            'notes': notes,
            'timestamp': datetime.now().isoformat()
        }
        
        print(f"[STATUS LOG] {log_entry}")
        return True
    except Exception as e:
        print(f"Error logging status change: {e}")
        return False
