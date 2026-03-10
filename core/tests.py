from datetime import date
from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import CustomUser
from .models import DoctorProfile, PatientProfile, Appointment, Prescription, MedicalRecord, TrimesterTracking


def make_doctor(username='doc_test'):
    user = CustomUser.objects.create_user(
        username=username, password='TestPass1!', role='doctor',
        first_name='Dr', last_name='Test'
    )
    profile = DoctorProfile.objects.create(
        user=user, specialization='obstetrician', experience_years=5, is_available=True
    )
    return user, profile


def make_patient(username='pat_test', doctor=None):
    user = CustomUser.objects.create_user(
        username=username, password='TestPass1!', role='patient',
        first_name='Pat', last_name='Test'
    )
    profile = PatientProfile.objects.create(
        user=user,
        last_menstrual_period=date(2025, 9, 1),
        due_date=date(2026, 6, 8),
        blood_group='O+',
        assigned_doctor=doctor,
    )
    return user, profile


class DoctorProfileModelTest(TestCase):
    def test_str(self):
        _, profile = make_doctor()
        self.assertIn('Dr', str(profile))
        self.assertIn('Obstetrician', str(profile))


class PatientProfileModelTest(TestCase):
    def test_trimester_calculation(self):
        _, patient = make_patient()
        # LMP = 2025-09-01, today is ~2026-03-10 -> ~27 weeks -> trimester 2 or 3
        trimester = patient.get_trimester()
        self.assertIn(trimester, [2, 3])

    def test_weeks_pregnant(self):
        _, patient = make_patient()
        weeks = patient.get_weeks_pregnant()
        self.assertIsNotNone(weeks)
        self.assertGreater(weeks, 0)

    def test_trimester_none_without_lmp(self):
        user = CustomUser.objects.create_user(username='nolmp', password='pass', role='patient')
        profile = PatientProfile.objects.create(user=user)
        self.assertIsNone(profile.get_trimester())
        self.assertIsNone(profile.get_weeks_pregnant())


class AppointmentModelTest(TestCase):
    def setUp(self):
        _, self.doctor = make_doctor()
        _, self.patient = make_patient(doctor=self.doctor)

    def test_create_appointment(self):
        appt = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            appointment_date=date(2026, 4, 1),
            appointment_time='10:00',
            reason='Routine checkup',
        )
        self.assertEqual(appt.status, Appointment.STATUS_PENDING)
        self.assertIn('Emma', str(appt)) if 'Emma' in str(appt) else self.assertIn('Pat', str(appt))


class PatientViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        _, self.doctor = make_doctor()
        self.patient_user, self.patient = make_patient(doctor=self.doctor)
        self.client.login(username='pat_test', password='TestPass1!')

    def test_patient_dashboard_accessible(self):
        response = self.client.get(reverse('patient_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'My Dashboard')

    def test_patient_book_appointment_get(self):
        response = self.client.get(reverse('patient_book_appointment'))
        self.assertEqual(response.status_code, 200)

    def test_patient_book_appointment_post(self):
        response = self.client.post(reverse('patient_book_appointment'), {
            'doctor': self.doctor.pk,
            'appointment_date': '2026-04-15',
            'appointment_time': '09:00',
            'reason': 'Prenatal visit',
        })
        self.assertRedirects(response, reverse('patient_appointments'))
        self.assertEqual(Appointment.objects.count(), 1)
        self.assertEqual(Appointment.objects.first().status, 'pending')

    def test_patient_cancel_appointment(self):
        appt = Appointment.objects.create(
            patient=self.patient, doctor=self.doctor,
            appointment_date=date(2026, 4, 15), appointment_time='09:00',
        )
        response = self.client.get(reverse('patient_cancel_appointment', args=[appt.pk]))
        self.assertRedirects(response, reverse('patient_appointments'))
        appt.refresh_from_db()
        self.assertEqual(appt.status, 'cancelled')

    def test_patient_prescriptions_page(self):
        response = self.client.get(reverse('patient_prescriptions'))
        self.assertEqual(response.status_code, 200)

    def test_patient_medical_records_page(self):
        response = self.client.get(reverse('patient_medical_records'))
        self.assertEqual(response.status_code, 200)

    def test_patient_trimester_tracking_get(self):
        response = self.client.get(reverse('patient_trimester_tracking'))
        self.assertEqual(response.status_code, 200)

    def test_patient_trimester_tracking_post(self):
        response = self.client.post(reverse('patient_trimester_tracking'), {
            'trimester': 3,
            'week_number': 27,
            'symptoms': 'Back pain, fatigue',
            'notes': 'Feeling generally okay',
        })
        self.assertRedirects(response, reverse('patient_trimester_tracking'))
        self.assertEqual(TrimesterTracking.objects.count(), 1)

    def test_doctor_cannot_access_patient_views(self):
        doc_user, _ = make_doctor(username='doc2_test')
        self.client.login(username='doc2_test', password='TestPass1!')
        response = self.client.get(reverse('patient_dashboard'))
        # _require_role redirects to 'dashboard', which further redirects to role dashboard
        self.assertRedirects(response, reverse('dashboard'), fetch_redirect_response=False)


class DoctorViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.doc_user, self.doctor = make_doctor()
        _, self.patient = make_patient(doctor=self.doctor)
        self.client.login(username='doc_test', password='TestPass1!')

    def test_doctor_dashboard_accessible(self):
        response = self.client.get(reverse('doctor_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Doctor Dashboard')

    def test_doctor_appointments_page(self):
        response = self.client.get(reverse('doctor_appointments'))
        self.assertEqual(response.status_code, 200)

    def test_doctor_patients_page(self):
        response = self.client.get(reverse('doctor_patients'))
        self.assertEqual(response.status_code, 200)

    def test_doctor_patient_detail(self):
        response = self.client.get(reverse('doctor_patient_detail', args=[self.patient.pk]))
        self.assertEqual(response.status_code, 200)

    def test_doctor_update_appointment(self):
        appt = Appointment.objects.create(
            patient=self.patient, doctor=self.doctor,
            appointment_date=date(2026, 4, 15), appointment_time='09:00',
        )
        response = self.client.post(
            reverse('doctor_update_appointment', args=[appt.pk]),
            {'status': 'confirmed', 'notes': 'Patient confirmed.'}
        )
        self.assertRedirects(response, reverse('doctor_appointments'))
        appt.refresh_from_db()
        self.assertEqual(appt.status, 'confirmed')

    def test_doctor_add_prescription(self):
        response = self.client.post(
            reverse('doctor_add_prescription', args=[self.patient.pk]),
            {
                'medications': 'Folic Acid 5mg - once daily\nIron 150mg - twice daily',
                'instructions': 'Take with food',
                'dietary_advice': 'Avoid processed foods',
                'follow_up_date': '2026-04-30',
            }
        )
        self.assertRedirects(response, reverse('doctor_patient_detail', args=[self.patient.pk]))
        self.assertEqual(Prescription.objects.count(), 1)

    def test_doctor_add_medical_record(self):
        response = self.client.post(
            reverse('doctor_add_medical_record', args=[self.patient.pk]),
            {
                'diagnosis': 'Normal pregnancy progress',
                'treatment': 'Continue prenatal vitamins',
                'weight_kg': '68.5',
                'blood_pressure': '120/80',
                'fetal_heart_rate': '148',
                'notes': 'All vitals normal',
            }
        )
        self.assertRedirects(response, reverse('doctor_patient_detail', args=[self.patient.pk]))
        self.assertEqual(MedicalRecord.objects.count(), 1)

    def test_patient_cannot_access_doctor_views(self):
        _, _ = make_patient(username='pat2_test')
        self.client.login(username='pat2_test', password='TestPass1!')
        response = self.client.get(reverse('doctor_dashboard'))
        self.assertRedirects(response, reverse('dashboard'), fetch_redirect_response=False)


class AdminViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = CustomUser.objects.create_user(
            username='admin_test', password='TestPass1!', role='admin',
            first_name='Admin', last_name='User'
        )
        _, self.doctor = make_doctor()
        _, self.patient = make_patient(doctor=self.doctor)
        self.client.login(username='admin_test', password='TestPass1!')

    def test_admin_dashboard_accessible(self):
        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Admin Dashboard')

    def test_admin_manage_doctors(self):
        response = self.client.get(reverse('admin_manage_doctors'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Dr')

    def test_admin_manage_patients(self):
        response = self.client.get(reverse('admin_manage_patients'))
        self.assertEqual(response.status_code, 200)

    def test_admin_view_appointments(self):
        response = self.client.get(reverse('admin_view_appointments'))
        self.assertEqual(response.status_code, 200)

    def test_admin_toggle_doctor(self):
        self.assertTrue(self.doctor.is_available)
        response = self.client.get(reverse('admin_toggle_doctor', args=[self.doctor.pk]))
        self.assertRedirects(response, reverse('admin_manage_doctors'))
        self.doctor.refresh_from_db()
        self.assertFalse(self.doctor.is_available)

    def test_non_admin_cannot_access_admin_views(self):
        _, _ = make_patient(username='pat3_test')
        self.client.login(username='pat3_test', password='TestPass1!')
        response = self.client.get(reverse('admin_dashboard'))
        self.assertRedirects(response, reverse('dashboard'), fetch_redirect_response=False)

