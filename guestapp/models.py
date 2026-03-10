from django.db import models

# Create your models here.
class tbl_login(models.Model):
    login_id = models.AutoField(primary_key=True)
    user_name = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    role = models.CharField(max_length=50)
    status = models.CharField(max_length=20)
