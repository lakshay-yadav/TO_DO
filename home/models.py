from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    isAdmin = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    user_description = models.TextField(null=True)


class PasswordResetOTP(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)


class Query(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    status = models.CharField(max_length=20,default="In Progress")
    remarks = models.TextField(default="We will soon take your issue. Please have some patience.")
    title = models.CharField(max_length=255)
    description = models.TextField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Donation(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    amount = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)


class todo(models.Model):
    user = models.ForeignKey(CustomUser,on_delete=models.CASCADE,null= True)
    title = models.CharField(max_length=255)
    description = models.TextField(default="Please add description",null=False)
    status = models.CharField(max_length=100,default="In Progress")
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
