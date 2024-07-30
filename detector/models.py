from django.db import models

# Create your models here.
class UserDetails(models.Model):
    user_name = models.CharField(max_length=100)
    user_email = models.EmailField()
    user_password = models.CharField(max_length=25,null=False,default='12345678')

