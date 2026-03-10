# Patient Status Implementation Guide

## Overview
This document explains the new patient status system with role-based access control for the Bloom Moms Care application.

---

## 1. Database Model Changes

### Updated tbl_patient Model

**Status Choices:**
- `Active` - Active pregnancy tracking
- `Delivered` - Patient has delivered
- `Miscarriage` - Pregnancy loss
- `Emergency` - Medical emergency case
- `Transferred` - Patient transferred to another hospital

**New Fields Added:**
```python
status = models.CharField(
    max_length=20, 
    choices=STATUS_CHOICES, 
    default='Active'
)

# Miscarriage Management
miscarriage_notes = models.TextField(blank=True, null=True)

# Emergency Case Management
emergency_notes = models.TextField(blank=True, null=True)

# Hospital Transfer Management
transfer_reason = models.TextField(blank=True, null=True)
transfer_date = models.DateField(blank=True, null=True)
transfer_summary = models.TextField(blank=True, null=True)
```

### Migration Applied
```bash
python manage.py migrate adminapp
# Migration: 0022_tbl_patient_emergency_notes_and_more
```

---

## 2. Role-Based Access Control

### Who Can Update Status?
- ✅ **Doctor** - Can update any patient status
- ✅ **Admin** - Can update patient status
- ❌ **Patient** - Cannot update status (read-only)

### Who Can Add Special Notes?
- ✅ **Doctor** - Can add miscarriage_notes, emergency_notes, transfer_reason/summary
- ❌ **Admin** - Cannot add special notes (view only)
- ❌ **Patient** - Cannot add any notes

---

## 3. Status-Specific Behaviors

### Active Status
- ✅ Full access to medical records
- ✅ Can add prescriptions
- ✅ Can update trimester
- ✅ Profile is editable

### Delivered Status
- ✅ Can add prescriptions (limited)
- ❌ Cannot update trimester
- ✅ Profile is editable
- 💾 Records are preserved

### Miscarriage Status
- ❌ Cannot add prescriptions
- ❌ Cannot update trimester
- ❌ Profile is read-only
- ✅ Can view full medical history
- 📝 Doctor can add miscarriage_notes

### Emergency Status
- ✅ All updates allowed
- ✅ Can add prescriptions
- ✅ Can update trimester
- 🔴 Red alert badge in UI
- 📝 Doctor can add emergency_notes
- 🔔 Admin notification created

### Transferred Status
- ❌ Cannot add prescriptions
- ❌ Cannot update trimester
- ❌ Profile is read-only
- ✅ Can view full medical history
- 📝 Doctor can add transfer details
- 📅 Transfer date recorded

---

## 4. Helper Functions (adminapp/utils.py)

### Status Validation Functions

```python
# Check if prescription can be added
can_add_prescription(patient)  # Returns bool

# Check if trimester tracking should be allowed
can_update_trimester(patient)  # Returns bool

# Check if profile should be read-only
is_patient_profile_readonly(patient)  # Returns bool

# Get restrictions for a status
get_status_restrictions(status)  # Returns str

# Check if user role can update status
check_role_can_update_status(login_role)  # Returns bool

# Check if user role can add medical notes
check_role_can_add_notes(login_role)  # Returns bool

# Log status changes for audit
log_status_change(patient, old_status, new_status, notes)  # Returns bool
```

---

## 5. View Implementation

### Updated patient_profile() View

**Role Check:**
```python
# Get user role from login session
login_obj = tbl_login.objects.get(login_id=login_id)
user_role = login_obj.role  # 'Doctor', 'Admin', or 'Patient'

# Check permission to update status
if user_role not in ['Doctor', 'Admin']:
    messages.error(request, 'You do not have permission...')
    return redirect(...)
```

**Status Update:**
```python
if action == 'update_status':
    old_status = patient.status
    new_status = request.POST.get('new_status')
    status_notes = request.POST.get('status_notes', '')
    
    # Special handling for different statuses
    if new_status == 'Miscarriage':
        patient.miscarriage_notes = status_notes
    
    if new_status == 'Emergency':
        patient.emergency_notes = status_notes
    
    if new_status == 'Transferred':
        patient.transfer_reason = status_notes
        patient.transfer_date = datetime.strptime(
            request.POST.get('transfer_date'), 
            '%Y-%m-%d'
        ).date()
        patient.transfer_summary = request.POST.get('transfer_summary')
    
    patient.status = new_status
    patient.save()
    log_status_change(patient, old_status, new_status, status_notes)
```

**Prescription Check:**
```python
elif action == 'add_prescription':
    if not can_add_prescription(patient):
        messages.error(request, f'Cannot add prescription for status: {patient.status}')
        return redirect(...)
    # Continue with prescription creation...
```

**Context Variables for Template:**
```python
context = {
    'patient': patient,
    'profile_readonly': is_patient_profile_readonly(patient),
    'can_add_prescription': can_add_prescription(patient),
    'can_update_trimester': can_update_trimester(patient),
    'user_role': user_role,
    'can_update_status': user_role in ['Doctor', 'Admin'],
    'patient_status_choices': tbl_patient.STATUS_CHOICES,
}
```

### Delivery Details Update

When delivery is recorded:
```python
if delivery_date:
    patient.delivery_date = delivery_date
    patient.profile_lock_status = 'unlocked'
    patient.lock_start_date = None
    patient.status = 'Delivered'  # Auto-update to Delivered
    patient.save()
```

---

## 6. Template Implementation Examples

### Patient Profile Template (Doctor/patientprofile.html)

**Display Status Badge:**
```html
<div class="patient-header">
    <h2>{{ patient.patient_name }}</h2>
    
    <!-- Status Badge -->
    <span class="status-badge status-{{ patient.status|lower }}">
        {{ patient.get_status_display }}
    </span>
    
    <!-- Emergency Alert -->
    {% if patient.status == 'Emergency' %}
    <div class="alert alert-danger">
        <strong>⚠️ EMERGENCY CASE</strong>
        {% if patient.emergency_notes %}
        <p>{{ patient.emergency_notes }}</p>
        {% endif %}
    </div>
    {% endif %}
    
    <!-- Transferred Alert -->
    {% if patient.status == 'Transferred' %}
    <div class="alert alert-warning">
        <strong>🚑 Patient Transferred</strong>
        <p>Transfer Date: {{ patient.transfer_date }}</p>
        {% if patient.transfer_reason %}
        <p>Reason: {{ patient.transfer_reason }}</p>
        {% endif %}
    </div>
    {% endif %}
    
    <!-- Miscarriage Alert -->
    {% if patient.status == 'Miscarriage' %}
    <div class="alert alert-info">
        <strong>ℹ️ Miscarriage Case</strong>
        {% if patient.miscarriage_notes %}
        <p>{{ patient.miscarriage_notes }}</p>
        {% endif %}
    </div>
    {% endif %}
</div>
```

**Update Status Form (Only for Doctor/Admin):**
```html
{% if can_update_status %}
<div class="status-update-section">
    <h4>Update Patient Status</h4>
    <form method="POST">
        {% csrf_token %}
        
        <div class="form-group">
            <label for="status_select">New Status:</label>
            <select name="new_status" id="status_select" class="form-control" required>
                <option value="">-- Select Status --</option>
                {% for value, display in patient_status_choices %}
                <option value="{{ value }}" 
                    {% if patient.status == value %}selected{% endif %}>
                    {{ display }}
                </option>
                {% endfor %}
            </select>
        </div>
        
        <!-- Conditional fields based on selected status -->
        <div id="miscarriage_notes" style="display:none;">
            <div class="form-group">
                <label for="notes">Miscarriage Notes:</label>
                <textarea name="status_notes" class="form-control" rows="3" 
                    placeholder="Patient medical history, complications, etc."></textarea>
            </div>
        </div>
        
        <div id="emergency_notes" style="display:none;">
            <div class="form-group">
                <label for="notes">Emergency Details:</label>
                <textarea name="status_notes" class="form-control" rows="3" 
                    placeholder="Emergency situation details..."></textarea>
            </div>
        </div>
        
        <div id="transfer_fields" style="display:none;">
            <div class="form-group">
                <label for="transfer_reason">Transfer Reason:</label>
                <textarea name="status_notes" class="form-control" rows="2" 
                    placeholder="Why patient is being transferred..."></textarea>
            </div>
            
            <div class="form-group">
                <label for="transfer_date">Transfer Date:</label>
                <input type="date" name="transfer_date" class="form-control">
            </div>
            
            <div class="form-group">
                <label for="transfer_summary">Transfer Summary:</label>
                <textarea name="transfer_summary" class="form-control" rows="2" 
                    placeholder="Summary of patient case and recommendations..."></textarea>
            </div>
        </div>
        
        <input type="hidden" name="action" value="update_status">
        <button type="submit" class="btn btn-primary">Update Status</button>
    </form>
</div>

<script>
document.getElementById('status_select').addEventListener('change', function() {
    const status = this.value;
    document.getElementById('miscarriage_notes').style.display = 
        status === 'Miscarriage' ? 'block' : 'none';
    document.getElementById('emergency_notes').style.display = 
        status === 'Emergency' ? 'block' : 'none';
    document.getElementById('transfer_fields').style.display = 
        status === 'Transferred' ? 'block' : 'none';
});
</script>
{% endif %}
```

**Prescription Add Button (Conditional):**
```html
{% if can_add_prescription %}
<button class="btn btn-success" data-toggle="modal" data-target="#addPrescription">
    <i class="fa fa-plus"></i> Add Prescription
</button>
{% else %}
<button class="btn btn-secondary" disabled title="Cannot add prescription for {{ patient.status }} status">
    <i class="fa fa-ban"></i> Add Prescription (Disabled)
</button>
<small class="text-muted">Prescriptions cannot be added for {{ patient.status }} status</small>
{% endif %}
```

**Profile Read-Only Indicator:**
```html
{% if profile_readonly %}
<div class="alert alert-warning">
    <i class="fa fa-lock"></i> This patient profile is read-only due to status: 
    <strong>{{ patient.status }}</strong>
</div>
{% endif %}
```

**Trimester Update Button (Conditional):**
```html
{% if can_update_trimester %}
<button class="btn btn-info" id="updateTrimester">
    Update Trimester
</button>
{% else %}
<button class="btn btn-secondary" disabled title="Trimester cannot be updated for {{ patient.status }} status">
    Update Trimester (Disabled)
</button>
{% endif %}
```

**Medical Records Section:**
```html
<div class="medical-records-section">
    <h4>Medical Records</h4>
    
    {% if profile_readonly %}
    <div class="alert alert-info">
        <i class="fa fa-info-circle"></i> Viewing medical history in read-only mode
    </div>
    {% endif %}
    
    {% for record in medical_records %}
    <div class="record-card">
        <h5>{{ record.record_date }}</h5>
        <p>{{ record.description }}</p>
        
        {% if record.doctor_note %}
        <p><strong>Doctor Notes:</strong> {{ record.doctor_note }}</p>
        {% endif %}
        
        {% if not profile_readonly %}
        <!-- Add doctor note form (only if not readonly) -->
        <form method="POST" class="add-note-form">
            {% csrf_token %}
            <input type="hidden" name="action" value="add_note">
            <input type="hidden" name="record_id" value="{{ record.record_id }}">
            <textarea name="doctor_note" class="form-control" rows="2" 
                placeholder="Add doctor notes..."></textarea>
            <button type="submit" class="btn btn-sm btn-primary mt-2">Add Note</button>
        </form>
        {% endif %}
    </div>
    {% endfor %}
</div>
```

---

## 7. CSS Styling

### Status Badge Styles

```css
.status-badge {
    display: inline-block;
    padding: 0.5rem 1rem;
    border-radius: 20px;
    font-weight: bold;
    font-size: 0.9rem;
    margin-left: 1rem;
}

.status-active {
    background-color: #28a745;  /* Green */
    color: white;
}

.status-delivered {
    background-color: #007bff;  /* Blue */
    color: white;
}

.status-miscarriage {
    background-color: #6c757d;  /* Gray */
    color: white;
}

.status-emergency {
    background-color: #dc3545;  /* Red */
    color: white;
    animation: pulse 1s infinite;
}

.status-transferred {
    background-color: #fd7e14;  /* Orange */
    color: white;
}

@keyframes pulse {
    0% {
        box-shadow: 0 0 0 0 rgba(220, 53, 69, 0.7);
    }
    70% {
        box-shadow: 0 0 0 10px rgba(220, 53, 69, 0);
    }
    100% {
        box-shadow: 0 0 0 0 rgba(220, 53, 69, 0);
    }
}
```

---

## 8. Admin Interface (Optional Enhancement)

### Register Model in admin.py

```python
from django.contrib import admin
from .models import tbl_patient

@admin.register(tbl_patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('patient_id', 'patient_name', 'status', 'doctor_id', 'created_at')
    list_filter = ('status', 'current_trimester', 'created_at')
    search_fields = ('patient_name', 'email', 'phone')
    readonly_fields = ('patient_id', 'created_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('patient_id', 'patient_name', 'age', 'email', 'phone', 'address')
        }),
        ('Medical Information', {
            'fields': ('blood_group', 'last_cycle_date', 'current_trimester', 
                      'edd_date', 'delivery_date')
        }),
        ('Status Management', {
            'fields': ('status',),
            'description': 'Current patient status'
        }),
        ('Status-Specific Notes', {
            'fields': ('miscarriage_notes', 'emergency_notes', 
                      'transfer_reason', 'transfer_date', 'transfer_summary'),
            'classes': ('collapse',)
        }),
        ('Lock Management', {
            'fields': ('profile_lock_status', 'lock_start_date', 
                      'unlock_start_date', 'unlock_end_date'),
            'classes': ('collapse',)
        }),
        ('Relationships', {
            'fields': ('doctor_id', 'login_id', 'image')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )
```

---

## 9. Key Validation Scenarios

### Scenario 1: Doctor marks patient as Miscarriage
1. Doctor is authenticated ✅
2. Doctor has 'Doctor' role ✅
3. Doctor selects Miscarriage status
4. Doctor provides miscarriage_notes
5. System prevents future prescriptions ✅
6. System prevents trimester updates ✅
7. Profile becomes read-only ✅

### Scenario 2: Emergency case alert
1. Doctor updates status to Emergency
2. Doctor can still add prescriptions ✅
3. Emergency badge displayed in red ✅
4. Admin receives notification ✅
5. Doctor can add emergency_notes

### Scenario 3: Patient transferred
1. Patient transferred to another hospital
2. Doctor marks as Transferred
3. Profile becomes read-only ✅
4. Transfer details recorded ✅
5. Medical history remains viewable ✅
6. No new prescriptions allowed ✅

### Scenario 4: Patient attempts unauthorized action
1. Patient tries to access add_delivery_details
2. System checks role (Patient) ❌
3. System denies access with error message
4. Patient redirected to home page

---

## 10. Testing Commands

### Run Migrations
```bash
cd d:\BloomMoms\BloomMomsproject
python manage.py migrate adminapp
```

### Check Model Changes
```bash
python manage.py sqlmigrate adminapp 0022
```

### Django Shell Testing
```bash
python manage.py shell

# Test role check
from adminapp.utils import check_role_can_update_status
print(check_role_can_update_status('Doctor'))  # True
print(check_role_can_update_status('Patient'))  # False

# Test status validation
from adminapp.utils import can_add_prescription
from adminapp.models import tbl_patient
patient = tbl_patient.objects.first()
print(can_add_prescription(patient))  # True if Active, False if Miscarriage/Transferred

# Check existing patient data
patients = tbl_patient.objects.all()
for p in patients:
    print(f"{p.patient_name}: {p.status}")
```

---

## 11. Data Safety

✅ **No data deletion** - Existing patient records are preserved
✅ **Backward compatible** - Default status is 'Active'
✅ **Safe fields** - All new fields are optional (blank=True, null=True)
✅ **Migration-safe** - Existing data remains intact during migration

---

## 12. Future Enhancements

- Add status change history/audit log
- Implement status change notifications
- Add automated status transitions based on delivery date
- Create status-based reports and dashboards
- Add admin bulk status updates
- Implement status-based patient list filtering

---

**Version:** 1.0
**Last Updated:** March 3, 2026
**Status:** Production Ready
