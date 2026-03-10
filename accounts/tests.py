from django.test import TestCase, Client
from django.urls import reverse
from .models import CustomUser


class CustomUserModelTest(TestCase):
    def setUp(self):
        self.admin = CustomUser.objects.create_user(
            username='testadmin', password='pass', role='admin', first_name='Test', last_name='Admin'
        )
        self.doctor = CustomUser.objects.create_user(
            username='testdoc', password='pass', role='doctor', first_name='Jane', last_name='Doe'
        )
        self.patient = CustomUser.objects.create_user(
            username='testpat', password='pass', role='patient', first_name='Alice', last_name='Smith'
        )

    def test_role_helpers(self):
        self.assertTrue(self.admin.is_admin_user())
        self.assertFalse(self.admin.is_doctor())
        self.assertFalse(self.admin.is_patient())
        self.assertTrue(self.doctor.is_doctor())
        self.assertTrue(self.patient.is_patient())

    def test_str_repr(self):
        self.assertIn('Admin', str(self.admin))
        self.assertIn('Doctor', str(self.doctor))
        self.assertIn('Patient', str(self.patient))

    def test_default_role_is_patient(self):
        user = CustomUser.objects.create_user(username='newuser', password='pass')
        self.assertEqual(user.role, CustomUser.ROLE_PATIENT)


class AuthViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.patient = CustomUser.objects.create_user(
            username='patuser', password='TestPass1!', role='patient', first_name='Pat', last_name='Test'
        )

    def test_login_page_get(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Bloom Moms Care')

    def test_login_success_redirects_to_dashboard(self):
        response = self.client.post(reverse('login'), {'username': 'patuser', 'password': 'TestPass1!'})
        # Dashboard view redirects patients to patient_dashboard, so use fetch_redirect_response=False
        self.assertRedirects(response, reverse('dashboard'), fetch_redirect_response=False)

    def test_login_failure(self):
        response = self.client.post(reverse('login'), {'username': 'patuser', 'password': 'wrongpass'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid username or password')

    def test_register_page_get(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)

    def test_register_creates_patient(self):
        data = {
            'username': 'newpatient',
            'first_name': 'New',
            'last_name': 'Patient',
            'email': 'new@test.com',
            'phone': '1234567890',
            'password1': 'SecurePass1!',
            'password2': 'SecurePass1!',
        }
        response = self.client.post(reverse('register'), data)
        self.assertRedirects(response, reverse('dashboard'), fetch_redirect_response=False)
        user = CustomUser.objects.get(username='newpatient')
        self.assertEqual(user.role, CustomUser.ROLE_PATIENT)

    def test_logout_requires_login(self):
        response = self.client.get(reverse('logout'))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('logout')}")

    def test_dashboard_redirects_unauthenticated(self):
        response = self.client.get(reverse('dashboard'))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('dashboard')}")

    def test_patient_dashboard_redirect(self):
        self.client.login(username='patuser', password='TestPass1!')
        response = self.client.get(reverse('dashboard'))
        self.assertRedirects(response, reverse('patient_dashboard'))

    def test_doctor_dashboard_redirect(self):
        doc = CustomUser.objects.create_user(
            username='docuser', password='TestPass1!', role='doctor'
        )
        self.client.login(username='docuser', password='TestPass1!')
        response = self.client.get(reverse('dashboard'))
        self.assertRedirects(response, reverse('doctor_dashboard'), fetch_redirect_response=False)

    def test_admin_dashboard_redirect(self):
        admin = CustomUser.objects.create_user(
            username='adminuser', password='TestPass1!', role='admin'
        )
        self.client.login(username='adminuser', password='TestPass1!')
        response = self.client.get(reverse('dashboard'))
        self.assertRedirects(response, reverse('admin_dashboard'))

