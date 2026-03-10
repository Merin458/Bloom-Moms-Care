#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BloomMomsproject.settings')
django.setup()

from django.core.mail import send_mail
from django.conf import settings

print("=" * 50)
print("EMAIL CONFIGURATION TEST")
print("=" * 50)
print(f"Email Backend: {settings.EMAIL_BACKEND}")
print(f"Email Host: {settings.EMAIL_HOST}")
print(f"Email Port: {settings.EMAIL_PORT}")
print(f"Use TLS: {settings.EMAIL_USE_TLS}")
print(f"Email User: {settings.EMAIL_HOST_USER}")
print(f"Default From Email: {settings.DEFAULT_FROM_EMAIL}")
print("=" * 50)

try:
    result = send_mail(
        'TEST - Bloom Moms Care Email System',
        'Hello!\n\nThis is a test email from your Bloom Moms Care system.\n\nIf you receive this, your email configuration is working correctly!\n\nBest regards,\nBloom Moms Care Team',
        settings.DEFAULT_FROM_EMAIL,
        ['bloommomscare@gmail.com'],
        fail_silently=False
    )
    print(f"✓ SUCCESS! Test email sent. Result code: {result}")
except Exception as e:
    print(f"✗ ERROR! Email failed to send:")
    print(f"Error type: {type(e).__name__}")
    print(f"Error message: {str(e)}")
    import traceback
    print("\nFull traceback:")
    traceback.print_exc()

print("=" * 50)
