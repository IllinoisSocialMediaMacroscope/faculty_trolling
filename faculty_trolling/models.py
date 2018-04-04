from django.db import models
from django.contrib.auth.models import User


class Proccess(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    pid = models.CharField(max_length = 100, unique=True, null=False)

class Twitter(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    access_key = models.CharField(max_length=100)
    access_token = models.CharField(max_length=100)
    oauth_token = models.CharField(max_length=100,null=False)
    oauth_token_secret = models.CharField(max_length=100,null=False)