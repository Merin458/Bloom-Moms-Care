# Complete Patient Profile Template Example

This file contains example HTML/Django template code for implementing the patient status system.

## File: Templates/Doctor/patientprofile.html

```html
{% extends 'Doctor/base.html' %}
{% load static %}

{% block title %}Patient Profile - {{ patient.patient_name }}{% endblock %}

{% block content %}
<div class="container-fluid mt-4">
    
    <!-- ==================== PATIENT HEADER ==================== -->
    <div class="row mb-4">
        <div class="col-md-12">
            <div class="card">
                <div class="card-header bg-primary text-white">
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <h3 class="mb-0">{{ patient.patient_name }}</h3>
                            <small>Patient ID: {{ patient.patient_id }}</small>
                        </div>
                        
                        <!-- Status Badge -->
                        <span class="status-badge status-{{ patient.status|lower }}">
                            {{ patient.get_status_display }}
                        </span>
                    </div>
                </div>
                
                <div class="card-body">
                    <!-- Emergency Alert -->
                    {% if patient.status == 'Emergency' %}
                    <div class="alert alert-danger alert-dismissible fade show" role="alert">
                        <strong><i class="fa fa-exclamation-triangle"></i> EMERGENCY CASE</strong>
                        {% if patient.emergency_notes %}
                        <p class="mb-0 mt-2">{{ patient.emergency_notes }}</p>
                        {% endif %}
                        <button type="button" class="close" data-dismiss="alert">
                            <span>&times;</span>
                        </button>
                    </div>
                    {% endif %}
                    
                    <!-- Miscarriage Alert -->
                    {% if patient.status == 'Miscarriage' %}
                    <div class="alert alert-info alert-dismissible fade show" role="alert">
                        <strong><i class="fa fa-info-circle"></i> Miscarriage Case</strong>
                        {% if patient.miscarriage_notes %}
                        <p class="mb-0 mt-2">{{ patient.miscarriage_notes }}</p>
                        {% endif %}
                        <button type="button" class="close" data-dismiss="alert">
                            <span>&times;</span>
                        </button>
                    </div>
                    {% endif %}
                    
                    <!-- Transferred Alert -->
                    {% if patient.status == 'Transferred' %}
                    <div class="alert alert-warning alert-dismissible fade show" role="alert">
                        <strong><i class="fa fa-hospital-o"></i> Patient Transferred</strong>
                        <br>
                        <strong>Transfer Date:</strong> {{ patient.transfer_date|date:"d M Y" }}
                        {% if patient.transfer_reason %}
                        <br><strong>Reason:</strong> {{ patient.transfer_reason }}
                        {% endif %}
                        {% if patient.transfer_summary %}
                        <br><strong>Summary:</strong> {{ patient.transfer_summary }}
                        {% endif %}
                        <button type="button" class="close" data-dismiss="alert">
                            <span>&times;</span>
                        </button>
                    </div>
                    {% endif %}
                    
                    <!-- Read-Only Indicator -->
                    {% if profile_readonly %}
                    <div class="alert alert-secondary">
                        <i class="fa fa-lock"></i> <strong>Read-Only Profile</strong>
                        <br>Medical records cannot be modified for {{ patient.get_status_display }} status.
                    </div>
                    {% endif %}
                    
                    <!-- Basic Information -->
                    <div class="row mt-3">
                        <div class="col-md-6">
                            <p><strong>Age:</strong> {{ patient.age }} years</p>
                            <p><strong>Phone:</strong> {{ patient.phone }}</p>
                            <p><strong>Email:</strong> {{ patient.email }}</p>
                        </div>
                        <div class="col-md-6">
                            <p><strong>Blood Group:</strong> {{ patient.blood_group }}</p>
                            <p><strong>Current Trimester:</strong> {{ patient.current_trimester }}</p>
                            <p><strong>EDD:</strong> {{ patient.edd_date|date:"d M Y" }}</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <!-- ==================== STATUS UPDATE SECTION ==================== -->
    {% if can_update_status %}
    <div class="row mb-4">
        <div class="col-md-12">
            <div class="card border-primary">
                <div class="card-header bg-light">
                    <h5 class="mb-0">
                        <i class="fa fa-edit"></i> Update Patient Status
                        <small class="text-muted">(Doctor/Admin Only)</small>
                    </h5>
                </div>
                <div class="card-body">
                    <form method="POST" id="statusForm" class="form-inline">
                        {% csrf_token %}
                        
                        <div class="form-group mr-3 mb-2 w-100">
                            <label for="new_status" class="mr-2">New Status:</label>
                            <select name="new_status" id="new_status" 
                                    class="form-control" required 
                                    onchange="updateStatusFields()">
                                <option value="">-- Select Status --</option>
                                {% for value, display in patient_status_choices %}
                                <option value="{{ value }}" 
                                    {% if patient.status == value %}selected{% endif %}>
                                    {{ display }}
                                </option>
                                {% endfor %}
                            </select>
                        </div>
                        
                        <!-- Generic Notes Field -->
                        <div class="form-group w-100 mt-3" id="notesField" style="display:none;">
                            <label for="status_notes">Notes:</label>
                            <textarea name="status_notes" id="status_notes" 
                                    class="form-control" rows="3" 
                                    placeholder="Enter relevant notes..."></textarea>
                        </div>
                        
                        <!-- Specific Fields for Transferred Status -->
                        <div id="transferFields" style="display:none;" class="w-100">
                            <div class="form-group mt-3">
                                <label for="transfer_date">Transfer Date:</label>
                                <input type="date" name="transfer_date" id="transfer_date" 
                                       class="form-control">
                            </div>
                            
                            <div class="form-group mt-3">
                                <label for="transfer_summary">Transfer Summary:</label>
                                <textarea name="transfer_summary" id="transfer_summary" 
                                        class="form-control" rows="3" 
                                        placeholder="Summary of patient case..."></textarea>
                            </div>
                        </div>
                        
                        <input type="hidden" name="action" value="update_status">
                        <button type="submit" class="btn btn-primary mt-3 w-100">
                            <i class="fa fa-save"></i> Update Status
                        </button>
                    </form>
                </div>
            </div>
        </div>
    </div>
    
    <script>
    function updateStatusFields() {
        const status = document.getElementById('new_status').value;
        const notesField = document.getElementById('notesField');
        const transferFields = document.getElementById('transferFields');
        const notesLabel = document.querySelector('label[for="status_notes"]');
        
        // Reset visibility
        notesField.style.display = 'none';
        transferFields.style.display = 'none';
        
        // Show fields based on selected status
        if (status === 'Miscarriage') {
            notesField.style.display = 'block';
            notesLabel.textContent = 'Miscarriage Notes:';
            document.getElementById('status_notes').placeholder = 
                'Enter medical history and details...';
        } else if (status === 'Emergency') {
            notesField.style.display = 'block';
            notesLabel.textContent = 'Emergency Details:';
            document.getElementById('status_notes').placeholder = 
                'Enter emergency situation details...';
        } else if (status === 'Transferred') {
            notesField.style.display = 'block';
            transferFields.style.display = 'block';
            notesLabel.textContent = 'Transfer Reason:';
            document.getElementById('status_notes').placeholder = 
                'Why is patient being transferred?';
        }
    }
    </script>
    {% endif %}
    
    <!-- ==================== MEDICAL RECORDS SECTION ==================== -->
    <div class="row mb-4">
        <div class="col-md-12">
            <div class="card">
                <div class="card-header bg-success text-white">
                    <h5 class="mb-0">
                        <i class="fa fa-file-medical"></i> Medical Records
                    </h5>
                </div>
                <div class="card-body">
                    {% if profile_readonly %}
                    <div class="alert alert-info mb-3">
                        <i class="fa fa-eye"></i> Viewing medical history in read-only mode
                    </div>
                    {% endif %}
                    
                    {% if medical_records %}
                        {% for record in medical_records %}
                        <div class="card mb-3 border-left-danger">
                            <div class="card-header bg-light">
                                <div class="d-flex justify-content-between">
                                    <strong>Record Date: {{ record.record_date|date:"d M Y" }}</strong>
                                    <span class="badge badge-info">
                                        {{ record.uploaded_by }}
                                    </span>
                                </div>
                            </div>
                            <div class="card-body">
                                <p><strong>Description:</strong> {{ record.description }}</p>
                                
                                {% if record.patient_uploaded_file %}
                                <p>
                                    <strong>Patient File:</strong>
                                    <a href="{{ record.patient_uploaded_file.url }}" 
                                       class="btn btn-sm btn-info" target="_blank">
                                        <i class="fa fa-download"></i> Download
                                    </a>
                                </p>
                                {% endif %}
                                
                                {% if record.admin_uploaded_file %}
                                <p>
                                    <strong>Admin File:</strong>
                                    <a href="{{ record.admin_uploaded_file.url }}" 
                                       class="btn btn-sm btn-info" target="_blank">
                                        <i class="fa fa-download"></i> Download
                                    </a>
                                </p>
                                {% endif %}
                                
                                {% if record.doctor_note %}
                                <div class="alert alert-light border-left-info">
                                    <strong>Doctor's Note:</strong>
                                    <p class="mb-0">{{ record.doctor_note }}</p>
                                </div>
                                {% endif %}
                                
                                <!-- Add Doctor Note Form (if not read-only) -->
                                {% if not profile_readonly and not record.doctor_note %}
                                <form method="POST" class="mt-3">
                                    {% csrf_token %}
                                    <input type="hidden" name="action" value="add_doctor_note">
                                    <input type="hidden" name="record_id" value="{{ record.record_id }}">
                                    
                                    <div class="form-group">
                                        <label for="doctor_note_{{ record.record_id }}">Add Doctor Note:</label>
                                        <textarea name="doctor_note" 
                                                id="doctor_note_{{ record.record_id }}" 
                                                class="form-control" rows="2" 
                                                placeholder="Enter your medical notes..."></textarea>
                                    </div>
                                    <button type="submit" class="btn btn-sm btn-success">
                                        <i class="fa fa-save"></i> Save Note
                                    </button>
                                </form>
                                {% endif %}
                            </div>
                        </div>
                        {% endfor %}
                    {% else %}
                    <div class="alert alert-secondary">
                        No medical records available.
                    </div>
                    {% endif %}
                </div>
            </div>
        </div>
    </div>
    
    <!-- ==================== PRESCRIPTIONS SECTION ==================== -->
    <div class="row mb-4">
        <div class="col-md-12">
            <div class="card">
                <div class="card-header bg-info text-white d-flex justify-content-between align-items-center">
                    <h5 class="mb-0">
                        <i class="fa fa-pills"></i> Prescriptions
                    </h5>
                    
                    <!-- Add Prescription Button -->
                    {% if can_add_prescription %}
                    <button class="btn btn-success btn-sm" data-toggle="modal" 
                            data-target="#addPrescription">
                        <i class="fa fa-plus"></i> Add Prescription
                    </button>
                    {% else %}
                    <button class="btn btn-secondary btn-sm" disabled 
                            title="Cannot add prescription for {{ patient.get_status_display }} status">
                        <i class="fa fa-ban"></i> Add Prescription (Disabled)
                    </button>
                    {% endif %}
                </div>
                <div class="card-body">
                    {% if not can_add_prescription %}
                    <div class="alert alert-warning mb-3">
                        <i class="fa fa-exclamation-circle"></i> 
                        Prescriptions cannot be added for <strong>{{ patient.get_status_display }}</strong> status.
                    </div>
                    {% endif %}
                    
                    {% if prescriptions %}
                        {% for prescription in prescriptions %}
                        <div class="card mb-3">
                            <div class="card-header bg-light">
                                <strong>Dr. {{ prescription.doctor.doctor_name }}</strong> - 
                                {{ prescription.prescription_date|date:"d M Y" }}
                            </div>
                            <div class="card-body">
                                <p><strong>Diagnosis:</strong> {{ prescription.diagnosis }}</p>
                                <p><strong>Medicines:</strong> {{ prescription.medicines }}</p>
                                <p><strong>Dosage:</strong> {{ prescription.dosage }}</p>
                                {% if prescription.additional_notes %}
                                <p><strong>Notes:</strong> {{ prescription.additional_notes }}</p>
                                {% endif %}
                            </div>
                        </div>
                        {% endfor %}
                    {% else %}
                    <div class="alert alert-secondary">
                        No prescriptions available.
                    </div>
                    {% endif %}
                </div>
            </div>
        </div>
    </div>
    
    <!-- ==================== VISIT HISTORY SECTION ==================== -->
    <div class="row mb-4">
        <div class="col-md-12">
            <div class="card">
                <div class="card-header bg-warning text-dark">
                    <h5 class="mb-0">
                        <i class="fa fa-calendar"></i> Latest Visit
                    </h5>
                </div>
                <div class="card-body">
                    {% if latest_visit %}
                    <div class="card">
                        <div class="card-header bg-light">
                            Visit Date: {{ latest_visit.visit_date|date:"d M Y" }}
                        </div>
                        <div class="card-body">
                            <p><strong>Weight:</strong> {{ latest_visit.weight }} kg</p>
                            <p><strong>Blood Pressure:</strong> {{ latest_visit.blood_pressure }}</p>
                            <p><strong>Health Status:</strong> {{ latest_visit.health_status }}</p>
                            <p><strong>Details:</strong> {{ latest_visit.details }}</p>
                            {% if latest_visit.next_visit_date %}
                            <p><strong>Next Visit:</strong> {{ latest_visit.next_visit_date|date:"d M Y" }}</p>
                            {% endif %}
                        </div>
                    </div>
                    {% else %}
                    <div class="alert alert-secondary">
                        No visit records available.
                    </div>
                    {% endif %}
                </div>
            </div>
        </div>
    </div>
    
    <!-- ==================== DELIVERY SECTION ==================== -->
    <div class="row mb-4">
        <div class="col-md-12">
            <div class="card">
                <div class="card-header bg-danger text-white d-flex justify-content-between align-items-center">
                    <h5 class="mb-0">
                        <i class="fa fa-baby"></i> Delivery Details
                    </h5>
                    <a href="{% url 'doctorapp:add_delivery_details' patient.patient_id %}" 
                       class="btn btn-light btn-sm">
                        <i class="fa fa-plus"></i> 
                        {% if delivery %}Update{% else %}Add{% endif %} Delivery
                    </a>
                </div>
                <div class="card-body">
                    {% if delivery %}
                    <div class="alert alert-success">
                        <strong>Delivery Recorded</strong> - {{ delivery.delivery_date|date:"d M Y" }}
                    </div>
                    <div class="row">
                        <div class="col-md-6">
                            <p><strong>Type:</strong> {{ delivery.delivery_type }}</p>
                            <p><strong>Baby Weight:</strong> {{ delivery.baby_weight }} kg</p>
                            <p><strong>Baby Condition:</strong> {{ delivery.baby_condition }}</p>
                        </div>
                        <div class="col-md-6">
                            <p><strong>Mother Condition:</strong> {{ delivery.mother_condition }}</p>
                            {% if delivery.remarks %}
                            <p><strong>Remarks:</strong> {{ delivery.remarks }}</p>
                            {% endif %}
                        </div>
                    </div>
                    {% else %}
                    <div class="alert alert-secondary">
                        No delivery details recorded.
                    </div>
                    {% endif %}
                </div>
            </div>
        </div>
    </div>

</div>

<!-- ==================== ADD PRESCRIPTION MODAL ==================== -->
<div class="modal fade" id="addPrescription" tabindex="-1" role="dialog">
    <div class="modal-dialog" role="document">
        <div class="modal-content">
            <div class="modal-header bg-info text-white">
                <h5 class="modal-title">Add Prescription</h5>
                <button type="button" class="close" data-dismiss="modal">
                    <span>&times;</span>
                </button>
            </div>
            <form method="POST">
                {% csrf_token %}
                <div class="modal-body">
                    <div class="form-group">
                        <label for="diagnosis">Diagnosis:</label>
                        <textarea name="diagnosis" id="diagnosis" 
                                class="form-control" rows="3" required></textarea>
                    </div>
                    
                    <div class="form-group">
                        <label for="medicines">Medicines:</label>
                        <textarea name="medicines" id="medicines" 
                                class="form-control" rows="3" required></textarea>
                    </div>
                    
                    <div class="form-group">
                        <label for="dosage">Dosage:</label>
                        <textarea name="dosage" id="dosage" 
                                class="form-control" rows="2"></textarea>
                    </div>
                    
                    <div class="form-group">
                        <label for="additional_notes">Additional Notes:</label>
                        <textarea name="additional_notes" id="additional_notes" 
                                class="form-control" rows="2"></textarea>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" 
                            data-dismiss="modal">Cancel</button>
                    <button type="submit" name="action" value="add_prescription" 
                            class="btn btn-success">
                        <i class="fa fa-save"></i> Add Prescription
                    </button>
                </div>
            </form>
        </div>
    </div>
</div>

{% endblock %}

<!-- ==================== STYLES ==================== -->
{% block extra_css %}
<style>
    .status-badge {
        display: inline-block;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: bold;
        font-size: 0.95rem;
    }
    
    .status-active {
        background-color: #28a745;
        color: white;
    }
    
    .status-delivered {
        background-color: #007bff;
        color: white;
    }
    
    .status-miscarriage {
        background-color: #6c757d;
        color: white;
    }
    
    .status-emergency {
        background-color: #dc3545;
        color: white;
        animation: pulse 1.5s infinite;
    }
    
    .status-transferred {
        background-color: #fd7e14;
        color: white;
    }
    
    @keyframes pulse {
        0%, 100% {
            opacity: 1;
            box-shadow: 0 0 0 0 rgba(220, 53, 69, 0.7);
        }
        50% {
            opacity: 0.8;
        }
        70% {
            box-shadow: 0 0 0 10px rgba(220, 53, 69, 0);
        }
    }
    
    .border-left-danger {
        border-left: 4px solid #dc3545 !important;
    }
    
    .border-left-info {
        border-left: 4px solid #17a2b8 !important;
    }
    
    .card {
        box-shadow: 0 0.125rem 0.25rem rgba(0,0,0,0.075);
    }
</style>
{% endblock %}
```

---

## Important Notes

1. **Update Path**: Save this file at `Templates/Doctor/patientprofile.html`
2. **Template Tags**: Make sure your base template includes all necessary CSS/JS libraries (Bootstrap, FontAwesome)
3. **CSRF Token**: Always include `{% csrf_token %}` in forms
4. **Context Variables**: Ensure your view provides all variables shown in the context dictionary
5. **Status Field Display**: Use `{{ patient.get_status_display }}` to show human-readable status

---

## Related View Code

Ensure your view (doctorapp/views.py - patient_profile) provides these context variables:

```python
context = {
    'patient': patient,
    'medical_records': medical_records,
    'prescriptions': prescriptions,
    'latest_visit': latest_visit,
    'delivery': delivery,
    'is_locked': is_locked_status,
    'profile_readonly': is_patient_profile_readonly(patient),
    'can_add_prescription': can_add_prescription(patient),
    'can_update_trimester': can_update_trimester(patient),
    'user_role': user_role,
    'can_update_status': user_role in ['Doctor', 'Admin'],
    'patient_status_choices': tbl_patient.STATUS_CHOICES,
}
```

