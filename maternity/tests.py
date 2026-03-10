from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from datetime import date, timedelta

from .models import (
    CustomUser, DoctorProfile, PatientProfile,
    Appointment, TrimsesterUpdate, Prescription,
    MedicalReport, ClinicalNote,
)


class UserModelTest(TestCase):
    def test_role_methods(self):
        admin = CustomUser(username='a', role='admin')
        doctor = CustomUser(username='d', role='doctor')
        patient = CustomUser(username='p', role='patient')
        self.assertTrue(admin.is_admin())
        self.assertTrue(doctor.is_doctor())
        self.assertTrue(patient.is_patient())
        self.assertFalse(admin.is_doctor())
        self.assertFalse(doctor.is_admin())

    def test_str_representation(self):
        u = CustomUser(username='testuser', first_name='Test', last_name='User', role='patient')
        self.assertIn('Test User', str(u))


class PatientProfileLockTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user('patientlock', password='pass', role='patient')
        self.patient = PatientProfile.objects.create(user=self.user)

    def test_profile_not_locked_without_delivery_date(self):
        self.assertFalse(self.patient.check_and_update_lock())

    def test_profile_locks_after_six_months(self):
        self.patient.actual_delivery_date = date.today() - timedelta(days=181)
        self.patient.save()
        self.assertTrue(self.patient.check_and_update_lock())
        self.patient.refresh_from_db()
        self.assertTrue(self.patient.is_locked)

    def test_profile_not_locked_before_six_months(self):
        self.patient.actual_delivery_date = date.today() - timedelta(days=90)
        self.patient.save()
        self.assertFalse(self.patient.check_and_update_lock())
        self.assertFalse(self.patient.is_locked)


class AuthViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = CustomUser.objects.create_user(
            'admin_test', password='pass123', role='admin'
        )
        self.admin.is_staff = True
        self.admin.save()

    def test_login_page_accessible(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)

    def test_redirect_unauthenticated_user(self):
        response = self.client.get(reverse('dashboard'))
        self.assertIn(response.status_code, [302, 301])

    def test_login_valid_credentials(self):
        response = self.client.post(reverse('login'), {
            'username': 'admin_test',
            'password': 'pass123',
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.redirect_chain[0][0].endswith('/dashboard/'))

    def test_login_invalid_credentials(self):
        response = self.client.post(reverse('login'), {
            'username': 'admin_test',
            'password': 'wrongpass',
        })
        self.assertEqual(response.status_code, 200)

    def test_logout_redirects(self):
        self.client.login(username='admin_test', password='pass123')
        response = self.client.get(reverse('logout'))
        self.assertRedirects(response, reverse('login'))


class AdminViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = CustomUser.objects.create_user(
            'admin_user', password='adminpass', role='admin',
            first_name='Admin', last_name='User'
        )
        self.client.login(username='admin_user', password='adminpass')

    def test_admin_dashboard(self):
        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Total Doctors')

    def test_admin_doctor_list(self):
        response = self.client.get(reverse('admin_doctor_list'))
        self.assertEqual(response.status_code, 200)

    def test_admin_add_doctor(self):
        response = self.client.post(reverse('admin_add_doctor'), {
            'username': 'new_doctor',
            'password': 'docpass123',
            'first_name': 'New',
            'last_name': 'Doctor',
            'email': 'doc@test.com',
            'phone': '555-0001',
            'specialization': 'gynecology',
            'experience_years': 5,
            'is_available': 'on',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(DoctorProfile.objects.filter(
            user__username='new_doctor'
        ).exists())

    def test_admin_patient_list(self):
        response = self.client.get(reverse('admin_patient_list'))
        self.assertEqual(response.status_code, 200)

    def test_admin_add_patient(self):
        doc_user = CustomUser.objects.create_user('doc2', password='d', role='doctor')
        doc = DoctorProfile.objects.create(user=doc_user, specialization='gynecology')
        response = self.client.post(reverse('admin_add_patient'), {
            'username': 'new_patient',
            'password': 'patpass123',
            'first_name': 'New',
            'last_name': 'Patient',
            'email': 'pat@test.com',
            'phone': '555-0002',
            'assigned_doctor': doc.pk,
            'blood_group': 'A+',
            'age': 28,
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(PatientProfile.objects.filter(
            user__username='new_patient'
        ).exists())

    def test_non_admin_cannot_access_admin_views(self):
        patient_user = CustomUser.objects.create_user(
            'p_user', password='ppass', role='patient'
        )
        PatientProfile.objects.create(user=patient_user)
        self.client.login(username='p_user', password='ppass')
        response = self.client.get(reverse('admin_dashboard'), follow=True)
        # Should end up on patient dashboard after chained redirects
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Dashboard')


class DoctorViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.doc_user = CustomUser.objects.create_user(
            'doc_test', password='docpass', role='doctor',
            first_name='Test', last_name='Doctor'
        )
        self.doctor = DoctorProfile.objects.create(
            user=self.doc_user, specialization='gynecology', is_available=True
        )
        self.client.login(username='doc_test', password='docpass')

        self.pat_user = CustomUser.objects.create_user(
            'pat_test', password='patpass', role='patient',
            first_name='Test', last_name='Patient'
        )
        self.patient = PatientProfile.objects.create(
            user=self.pat_user, assigned_doctor=self.doctor, age=25
        )

    def test_doctor_dashboard(self):
        response = self.client.get(reverse('doctor_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'My Patients')

    def test_doctor_patient_list(self):
        response = self.client.get(reverse('doctor_patient_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Patient')

    def test_doctor_patient_detail(self):
        response = self.client.get(
            reverse('doctor_patient_detail', kwargs={'pk': self.patient.pk})
        )
        self.assertEqual(response.status_code, 200)

    def test_doctor_add_prescription(self):
        response = self.client.post(
            reverse('doctor_add_prescription', kwargs={'patient_pk': self.patient.pk}),
            {
                'title': 'Test Prescription',
                'medications': 'Folic Acid 5mg',
                'date_prescribed': date.today().isoformat(),
            }
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Prescription.objects.filter(title='Test Prescription').exists())

    def test_doctor_add_trimester_update(self):
        response = self.client.post(
            reverse('doctor_add_trimester', kwargs={'patient_pk': self.patient.pk}),
            {
                'trimester_number': 1,
                'date_recorded': date.today().isoformat(),
                'health_notes': 'Patient doing well',
            }
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(TrimsesterUpdate.objects.filter(
            patient=self.patient, trimester_number=1
        ).exists())

    def test_doctor_add_clinical_note(self):
        response = self.client.post(
            reverse('doctor_add_clinical_note', kwargs={'patient_pk': self.patient.pk}),
            {
                'title': 'Initial Consultation',
                'note': 'Patient is healthy.',
                'date_noted': date.today().isoformat(),
            }
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(ClinicalNote.objects.filter(title='Initial Consultation').exists())

    def test_doctor_appointment_list(self):
        response = self.client.get(reverse('doctor_appointment_list'))
        self.assertEqual(response.status_code, 200)


class PatientViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.doc_user = CustomUser.objects.create_user(
            'doc_pat', password='docpass', role='doctor'
        )
        self.doctor = DoctorProfile.objects.create(
            user=self.doc_user, specialization='gynecology', is_available=True
        )
        self.pat_user = CustomUser.objects.create_user(
            'pat_login', password='patpass', role='patient',
            first_name='Login', last_name='Patient'
        )
        self.patient = PatientProfile.objects.create(
            user=self.pat_user, assigned_doctor=self.doctor,
            age=30, blood_group='O+',
            expected_delivery_date=date.today() + timedelta(days=60)
        )
        self.client.login(username='pat_login', password='patpass')

    def test_patient_dashboard(self):
        response = self.client.get(reverse('patient_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'My Dashboard')

    def test_patient_available_doctors(self):
        response = self.client.get(reverse('patient_available_doctors'))
        self.assertEqual(response.status_code, 200)

    def test_patient_locked_sees_only_gynecologists(self):
        # Create a non-gynecology doctor
        other_user = CustomUser.objects.create_user('otherdoc', password='p', role='doctor')
        DoctorProfile.objects.create(
            user=other_user, specialization='general', is_available=True
        )
        # Lock the patient
        self.patient.is_locked = True
        self.patient.actual_delivery_date = date.today() - timedelta(days=200)
        self.patient.save()
        response = self.client.get(reverse('patient_available_doctors'))
        self.assertEqual(response.status_code, 200)
        # Should only show gynecology doctors
        doctors = response.context['doctors']
        for doc in doctors:
            self.assertEqual(doc.specialization, 'gynecology')

    def test_patient_book_appointment(self):
        response = self.client.post(reverse('patient_book_appointment'), {
            'doctor': self.doctor.pk,
            'requested_date': (date.today() + timedelta(days=7)).isoformat(),
            'requested_time': '10:00',
            'reason': 'Regular checkup',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Appointment.objects.filter(
            patient=self.patient, doctor=self.doctor, status='pending'
        ).exists())

    def test_patient_appointments_list(self):
        Appointment.objects.create(
            patient=self.patient, doctor=self.doctor,
            requested_date=date.today() + timedelta(days=7),
            requested_time='10:00', status='pending'
        )
        response = self.client.get(reverse('patient_appointments'))
        self.assertEqual(response.status_code, 200)

    def test_patient_prescriptions(self):
        response = self.client.get(reverse('patient_prescriptions'))
        self.assertEqual(response.status_code, 200)

    def test_patient_reports(self):
        response = self.client.get(reverse('patient_reports'))
        self.assertEqual(response.status_code, 200)

    def test_patient_trimester_updates(self):
        response = self.client.get(reverse('patient_trimester_updates'))
        self.assertEqual(response.status_code, 200)

    def test_patient_clinical_notes(self):
        response = self.client.get(reverse('patient_clinical_notes'))
        self.assertEqual(response.status_code, 200)


class AppointmentTest(TestCase):
    def setUp(self):
        self.admin = CustomUser.objects.create_user(
            'admin_appt', password='adminpass', role='admin'
        )
        self.doc_user = CustomUser.objects.create_user('doc_appt', password='d', role='doctor')
        self.doctor = DoctorProfile.objects.create(
            user=self.doc_user, specialization='obstetrics', is_available=True
        )
        self.pat_user = CustomUser.objects.create_user('pat_appt', password='p', role='patient')
        self.patient = PatientProfile.objects.create(
            user=self.pat_user, assigned_doctor=self.doctor
        )
        self.appointment = Appointment.objects.create(
            patient=self.patient, doctor=self.doctor,
            requested_date=date.today() + timedelta(days=3),
            requested_time='09:00', status='pending', reason='Checkup'
        )

    def test_admin_can_update_appointment_status(self):
        client = Client()
        client.login(username='admin_appt', password='adminpass')
        response = client.post(
            reverse('admin_appointment_detail', kwargs={'pk': self.appointment.pk}),
            {
                'status': 'accepted',
                'admin_notes': 'Confirmed',
            }
        )
        self.assertEqual(response.status_code, 302)
        self.appointment.refresh_from_db()
        self.assertEqual(self.appointment.status, 'accepted')

    def test_admin_can_reschedule_appointment(self):
        client = Client()
        client.login(username='admin_appt', password='adminpass')
        new_date = date.today() + timedelta(days=10)
        response = client.post(
            reverse('admin_appointment_detail', kwargs={'pk': self.appointment.pk}),
            {
                'status': 'rescheduled',
                'scheduled_date': new_date.isoformat(),
                'scheduled_time': '14:00',
                'admin_notes': 'Rescheduled due to doctor unavailability',
            }
        )
        self.assertEqual(response.status_code, 302)
        self.appointment.refresh_from_db()
        self.assertEqual(self.appointment.status, 'rescheduled')
        self.assertEqual(self.appointment.scheduled_date, new_date)

    def test_doctor_can_mark_complete(self):
        self.appointment.status = 'accepted'
        self.appointment.save()
        client = Client()
        client.login(username='doc_appt', password='d')
        response = client.post(
            reverse('doctor_mark_appointment_complete', kwargs={'pk': self.appointment.pk})
        )
        self.assertEqual(response.status_code, 302)
        self.appointment.refresh_from_db()
        self.assertEqual(self.appointment.status, 'completed')
