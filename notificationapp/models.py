from django.db import models

class Notification(models.Model):
    USER_TYPE_CHOICES = [
        ('Admin', 'Admin'),
        ('Doctor', 'Doctor'),
        ('Patient', 'Patient'),
    ]
    
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)
    user_id = models.CharField(max_length=100)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'tbl_notification'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user_type} - {self.message[:50]}"
